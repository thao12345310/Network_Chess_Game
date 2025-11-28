# Vấn đề: Protocol Mismatch - Client không thể gửi Move

## 🚨 Vấn đề chính

**Client gửi format:**
```json
{
  "type": "MOVE",
  "from": "e2",
  "to": "e4",
  "game_id": "123",
  "session_token": "...",
  "timestamp": 1234567890
}
```

**Server chỉ nhận format:**
```json
{
  "action": "validate_move",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move": "e2e4"
}
```

**→ Server KHÔNG THỂ xử lý message từ client!**

---

## 🔍 Phân tích chi tiết

### Client Code (`GameClient.cpp` dòng 124-135):

```cpp
bool GameClient::sendMove(const std::string &fromPos, const std::string &toPos)
{
    Json::Value msg;
    msg["type"] = "MOVE";              // ← Field: "type"
    msg["game_id"] = currentGameId;
    msg["from"] = fromPos;             // ← "from": "e2"
    msg["to"] = toPos;                 // ← "to": "e4"
    msg["session_token"] = netClient->getSessionToken();
    msg["timestamp"] = static_cast<int>(std::time(nullptr));
    
    return netClient->sendMessage(msg);  // Gửi đến port 5001
}
```

**Message được gửi:**
```json
{
  "type": "MOVE",
  "game_id": "123",
  "from": "e2",
  "to": "e4",
  "session_token": "abc123",
  "timestamp": 1234567890
}
```

---

### Server Code (`NetworkInterface.cpp` + `logic_wrapper.py`):

**NetworkInterface nhận request:**
```cpp
std::string response = process_request(line);  // line = JSON string từ client
```

**process_request() gọi Python:**
```cpp
std::string command = "python logic_wrapper.py \"" + escaped_request + "\"";
// Gửi JSON string đến Python
```

**Python (`logic_wrapper.py`) xử lý:**
```python
req = json.loads(input_str)  # Parse JSON từ client
action = req.get('action')   # ← Tìm field "action"

if action == 'validate_move':  # ← Không match!
    # ...
```

**→ `req.get('action')` trả về `None` vì client gửi `"type": "MOVE"`, không phải `"action"`!**

---

## 📊 So sánh Protocol

| Aspect | Client Protocol | Server Protocol |
|--------|----------------|-----------------|
| **Field name** | `"type"` | `"action"` |
| **Move format** | `"from": "e2"`, `"to": "e4"` | `"move": "e2e4"` (UCI) |
| **FEN** | ❌ Không có | ✅ Bắt buộc |
| **Session** | ✅ `session_token` | ❌ Không có |
| **Game ID** | ✅ `game_id` | ❌ Không có |
| **Messages** | `MOVE`, `LOGIN`, `REGISTER`, `SEND_CHALLENGE`, etc. | `validate_move`, `calculate_elo`, `log_move`, etc. |

---

## ❌ Tại sao không hoạt động?

### Luồng hiện tại:

```
Client
  │
  │ Gửi: {"type": "MOVE", "from": "e2", "to": "e4", ...}
  │
  ▼
NetworkInterface::process_request()
  │
  │ Gửi đến Python: python logic_wrapper.py "{...}"
  │
  ▼
logic_wrapper.py
  │
  │ req.get('action') → None  ❌
  │
  │ Không match bất kỳ action nào
  │
  ▼
Response: {"status": "error", "message": "Unknown action: None"}
```

---

## ✅ Giải pháp

Có 2 cách:

### Giải pháp 1: Thêm handler trong NetworkInterface để chuyển đổi protocol

**Ý tưởng:** NetworkInterface nhận message từ client, chuyển đổi sang format mà logic_wrapper.py hiểu.

**Ví dụ:**
```cpp
std::string NetworkInterface::process_request(const std::string& request) {
    // Parse JSON
    Json::Value clientMsg = parseJson(request);
    std::string type = clientMsg["type"].asString();
    
    if (type == "MOVE") {
        // Cần lấy FEN hiện tại của game
        // Cần convert "from" + "to" → "e2e4" (UCI format)
        
        // Tạo request mới cho logic_wrapper
        Json::Value logicReq;
        logicReq["action"] = "validate_move";
        logicReq["fen"] = getCurrentFEN(clientMsg["game_id"]);
        logicReq["move"] = clientMsg["from"].asString() + clientMsg["to"].asString();
        
        // Gửi đến logic_wrapper.py
        return callLogicWrapper(logicReq);
    }
    // ... xử lý các types khác
}
```

**Vấn đề:** 
- Cần lưu FEN hiện tại của game (state management)
- Phức tạp hơn

---

### Giải pháp 2: Thêm action mới trong logic_wrapper.py để xử lý MOVE từ client

**Ý tưởng:** Thêm action `make_move` nhận format từ client, tự động xử lý FEN và validate.

**Ví dụ trong `logic_wrapper.py`:**
```python
elif action == 'make_move':  # Hoặc req.get('type') == 'MOVE'
    game_id = req.get('game_id')
    from_pos = req.get('from')  # "e2"
    to_pos = req.get('to')      # "e4"
    
    # Lấy FEN hiện tại từ database hoặc game state
    current_fen = get_game_fen(game_id)
    
    # Convert to UCI
    move_uci = from_pos + to_pos  # "e2e4"
    
    # Validate
    is_valid, next_fen = validate_move(current_fen, move_uci)
    
    if is_valid:
        # Lưu move vào DB
        player_id = get_current_player(game_id)
        insert_move(game_id, player_id, move_uci)
        
        # Update game FEN
        update_game_fen(game_id, next_fen)
        
        response = {
            "status": "success",
            "is_valid": True,
            "next_fen": next_fen
        }
    else:
        response = {
            "status": "error",
            "message": "Invalid move"
        }
```

**Vấn đề:**
- Cần lưu FEN trong database hoặc game state
- Cần biết player hiện tại đang chơi
- Cần xử lý nhiều logic hơn

---

### Giải pháp 3: Tạo Game Server riêng (Khuyến nghị)

**Ý tưởng:** Tách riêng:
- **Game Logic Server** (port 5001): Xử lý logic cờ vua thuần túy (`validate_move`, `calculate_elo`, etc.)
- **Game Server** (port khác, ví dụ 5000): Xử lý game protocol (`MOVE`, `LOGIN`, `REGISTER`, etc.)

**Game Server sẽ:**
1. Nhận message từ client (`{"type": "MOVE", ...}`)
2. Lấy game state (FEN, player turn, etc.)
3. Gọi Game Logic Server để validate
4. Update game state và database
5. Gửi response về client

**Luồng:**
```
Client
  │
  │ {"type": "MOVE", "from": "e2", "to": "e4"}
  │
  ▼
Game Server (port 5000)
  │
  │ 1. Lấy FEN hiện tại từ game state
  │ 2. Convert "e2" + "e4" → "e2e4"
  │ 3. Gọi Game Logic Server
  │
  ▼
Game Logic Server (port 5001)
  │
  │ {"action": "validate_move", "fen": "...", "move": "e2e4"}
  │
  ▼
Game Logic Server trả về: {"status": "success", "is_valid": true, "next_fen": "..."}
  │
  ▼
Game Server
  │
  │ 4. Lưu move vào DB
  │ 5. Update game state
  │ 6. Gửi update đến opponent
  │
  ▼
Client nhận: {"type": "MOVE_RESULT", "is_valid": true, ...}
```

---

## 🎯 Giải pháp nhanh nhất (Quick Fix)

**Thêm handler trực tiếp trong `logic_wrapper.py` để nhận format từ client:**

```python
def main():
    # ...
    req = json.loads(input_str)
    
    # Check cả "type" (từ client) và "action" (từ test)
    msg_type = req.get('type') or req.get('action')
    
    if msg_type == 'MOVE' or msg_type == 'validate_move':
        # Xử lý move request
        
        if msg_type == 'MOVE':
            # Format từ client
            game_id = req.get('game_id')
            from_pos = req.get('from')
            to_pos = req.get('to')
            move_uci = from_pos + to_pos
            
            # TODO: Lấy FEN hiện tại (cần implement)
            current_fen = get_current_fen_for_game(game_id)
            
        elif msg_type == 'validate_move':
            # Format từ test
            current_fen = req.get('fen')
            move_uci = req.get('move')
        
        # Validate
        is_valid, next_fen = validate_move(current_fen, move_uci)
        
        if is_valid and msg_type == 'MOVE':
            # Lưu vào DB
            player_id = get_current_player_id(game_id)  # TODO
            insert_move(game_id, player_id, move_uci)
            update_game_fen(game_id, next_fen)  # TODO
        
        response = {
            "status": "success",
            "is_valid": is_valid,
            "next_fen": next_fen
        }
    
    # ... xử lý các types khác
```

**Nhưng vẫn thiếu:**
- Hàm `get_current_fen_for_game()` - cần lưu FEN trong DB hoặc state
- Hàm `get_current_player_id()` - cần biết lượt của ai
- Hàm `update_game_fen()` - cần update state

---

## 📋 Tóm tắt

**Vấn đề:**
- Client gửi `{"type": "MOVE", "from": "e2", "to": "e4"}` 
- Server chỉ hiểu `{"action": "validate_move", "fen": "...", "move": "e2e4"}`
- → **Protocol không khớp!**

**Giải pháp:**
1. ✅ Thêm handler trong `logic_wrapper.py` để nhận cả `type` và `action`
2. ❌ Cần thêm: Lưu game state (FEN, current player) trong DB
3. ❌ Cần thêm: Các hàm get/update game state

**Khuyến nghị:** Tạo Game Server riêng để xử lý game protocol và state management.

