# Hướng dẫn Test RESIGN và DRAW OFFER trên UI

## ✅ Những gì đã có sẵn

### 1. UI Buttons (screen_game.py)
- ✅ Button "🏳️ Resign" 
- ✅ Button "🤝 Offer Draw"
- ✅ Confirmation dialogs

### 2. Client API (GameClient.cpp)
- ✅ `resign()` - Gửi GAME_RESIGN
- ✅ `offerDraw()` - Gửi DRAW_OFFER
- ✅ `acceptDraw()` - Gửi DRAW_ACCEPT
- ✅ `declineDraw()` - Gửi DRAW_DECLINE

### 3. Server Handler (NetworkInterface.cpp)
- ✅ GAME_RESIGN handler - Xử lý resign, update ELO
- ✅ DRAW_OFFER handler - Broadcast đến opponent

### 4. Python Logic (logic_wrapper.py)
- ✅ `resign_game` action - Update DB, calculate ELO
- ✅ `get_game_info` action - Get player IDs

---

## 🔧 Những gì vừa thêm

### 1. UI Callbacks (screen_game.py)
```python
# Added to setup_callbacks():
self.client.set_callback('GAME_END', self.on_game_end_msg)
self.client.set_callback('DRAW_OFFER_NOTIFY', self.on_draw_offer_received)

# New method:
def on_draw_offer_received(self, msg):
    # Shows popup asking to accept/decline draw
```

### 2. Network Client Methods (network_client.py)
```python
def accept_draw(self, game_id):
    return self.lib.client_accept_draw(self.handle) == 1

def decline_draw(self, game_id):
    return self.lib.client_decline_draw(self.handle) == 1
```

### 3. Client API Export (ClientAPI.h/cpp)
```cpp
int client_accept_draw(ClientHandle handle);
int client_decline_draw(ClientHandle handle);
```

---

## 📋 Để test được, cần:

### Step 1: Compile lại Client
```bash
cd client
make clean
make
```

### Step 2: Compile lại Server (nếu chưa)
```bash
cd server/src
make clean  
make
```

### Step 3: Start Server
```bash
cd server/src
./server
```

### Step 4: Chạy UI Client
```bash
cd ui
python app_main.py
```

---

## 🎮 Cách Test

### Test Scenario 1: RESIGN

**Player 1:**
1. Login vào server
2. Start/join game
3. Click button "🏳️ Resign"
4. Confirm trong dialog
5. ✅ Nhận GAME_END với result="loss"

**Player 2 (Opponent):**
1. Tự động nhận GAME_END với result="win"
2. Reason: "opponent_resigned"
3. ELO được update

### Test Scenario 2: DRAW OFFER

**Player 1 (Sender):**
1. Trong game, click "🤝 Offer Draw"
2. ✅ Nhận toast "Draw offer sent to opponent"
3. ✅ Nhận DRAW_OFFER_ACK từ server

**Player 2 (Receiver):**
1. ✅ Popup hiện: "Your opponent offers a draw. Do you accept?"
2. **Case A: Accept**
   - Click "Yes"
   - ✅ Gửi DRAW_ACCEPT
   - ✅ Cả 2 players nhận GAME_END với result="draw"
   - ELO updated (0.5 points each)
3. **Case B: Decline**
   - Click "No"
   - ✅ Gửi DRAW_DECLINE
   - Game continues normally

---

## 🐛 TODO - Implement Draw Accept Logic

Hiện tại server **chưa có handler cho DRAW_ACCEPT/DRAW_DECLINE**. Cần thêm vào `NetworkInterface.cpp`:

### Add to NetworkInterface.cpp:

```cpp
// DRAW_ACCEPT - Player accepts draw offer
else if (type == Protocol::MessageType::DRAW_ACCEPT || action == "DRAW_ACCEPT") {
    int game_id = get_json_int(request, "game_id");
    int my_id = 0;
    {
        std::lock_guard<std::mutex> lock(session_mutex);
        if (client_sessions.find(clientSocket) != client_sessions.end()) {
            my_id = client_sessions[clientSocket];
        }
    }
    
    if (my_id == 0 || game_id == 0) {
        return "{\"messageType\": \"ERROR\", \"responseCode\": 400, \"payload\": {\"reason\": \"Invalid request\"}}";
    }
    
    // Call Python to process draw acceptance
    std::string draw_req = "{\"action\": \"accept_draw\", \"game_id\": " + std::to_string(game_id) + "}";
    std::string draw_res = execute_logic_command(draw_req);
    
    // Parse response
    bool success = (draw_res.find("\"status\": \"success\"") != std::string::npos);
    
    if (success) {
        int white_id = get_json_int(draw_res, "white_id");
        int black_id = get_json_int(draw_res, "black_id");
        int white_elo = get_json_int(draw_res, "white_elo");
        int black_elo = get_json_int(draw_res, "black_elo");
        
        // Broadcast GAME_END to both players
        std::lock_guard<std::mutex> lock(session_mutex);
        
        for (auto const& [sock, pid] : client_sessions) {
            if (pid == white_id || pid == black_id) {
                int player_elo = (pid == white_id) ? white_elo : black_elo;
                std::string end_msg = "{\"messageType\": \"GAME_END\", \"responseCode\": 200, \"payload\": {"
                                     "\"game_id\": " + std::to_string(game_id) + ", "
                                     "\"result\": \"draw\", "
                                     "\"reason\": \"draw_accepted\", "
                                     "\"new_elo\": " + std::to_string(player_elo) + "}}";
                send(sock, end_msg.c_str(), static_cast<int>(end_msg.length()), 0);
                send(sock, "\n", 1, 0);
            }
        }
        
        return "{\"messageType\": \"GAME_END\", \"responseCode\": 200, \"payload\": {"
               "\"game_id\": " + std::to_string(game_id) + ", "
               "\"result\": \"draw\", "
               "\"reason\": \"draw_accepted\"}}";
    } else {
        return "{\"messageType\": \"ERROR\", \"responseCode\": 500, \"payload\": {\"reason\": \"Failed to accept draw\"}}";
    }
}

// DRAW_DECLINE - Player declines draw offer  
else if (type == Protocol::MessageType::DRAW_DECLINE || action == "DRAW_DECLINE") {
    // Just acknowledge - game continues
    int game_id = get_json_int(request, "game_id");
    return "{\"messageType\": \"DRAW_DECLINE_ACK\", \"responseCode\": 200, \"payload\": {"
           "\"game_id\": " + std::to_string(game_id) + ", "
           "\"status\": \"declined\"}}";
}
```

### Add to logic_wrapper.py:

```python
elif action == 'accept_draw':
    # Handle draw acceptance
    game_id = req.get('game_id')
    
    if not game_id:
        response = {"status": "error", "message": "Missing game_id"}
    else:
        try:
            # Get game info
            game_info = get_game_info(game_id)
            if not game_info:
                response = {"status": "error", "message": "Game not found"}
            else:
                white_id = game_info[1]
                black_id = game_info[2]
                
                # Update game result to draw (winner_id = NULL)
                update_game_result(
                    game_id,
                    None,  # No winner in draw
                    'FINISHED',
                    datetime.datetime.utcnow().isoformat()
                )
                
                # Calculate ELO for draw (0.5 points each)
                white_rating = get_player_rating(white_id)
                black_rating = get_player_rating(black_id)
                
                new_white_elo, new_black_elo = calculate_elo(
                    white_rating, 
                    black_rating, 
                    0.5  # Draw = 0.5 points each
                )
                
                # Update ELO in database
                update_both_players_elo(white_id, new_white_elo, black_id, new_black_elo)
                
                response = {
                    "status": "success",
                    "white_id": white_id,
                    "black_id": black_id,
                    "white_elo": new_white_elo,
                    "black_elo": new_black_elo
                }
                
        except Exception as e:
            response = {"status": "error", "message": f"Error accepting draw: {str(e)}"}
```

---

## 📊 Current Status

| Feature | UI | Client API | Server | Python Logic | Status |
|---------|-----|------------|--------|--------------|--------|
| Resign Button | ✅ | ✅ | ✅ | ✅ | **READY** |
| Resign Handler | ✅ | ✅ | ✅ | ✅ | **READY** |
| Draw Offer Button | ✅ | ✅ | ✅ | ✅ | **READY** |
| Draw Offer Handler | ✅ | ✅ | ✅ | ✅ | **READY** |
| Draw Accept/Decline UI | ✅ | ✅ | ⚠️ | ⚠️ | **NEED IMPL** |

⚠️ = Code đã có nhưng cần thêm handlers (xem section TODO trên)

---

## 🚀 Quick Start (Nếu đã compile)

```bash
# Terminal 1 - Server
cd server/src && ./server

# Terminal 2 - Player 1 UI
cd ui && python app_main.py

# Terminal 3 - Player 2 UI  
cd ui && python app_main.py

# Test:
# 1. Login both players
# 2. Start game (challenge or matchmaking)
# 3. Try resign or offer draw!
```

---

## 🎯 Summary

**RESIGN: 100% Ready ✅**
- UI có button
- Client gửi được message
- Server xử lý và update DB
- Broadcast kết quả đến cả 2 players

**DRAW OFFER: 90% Ready ⚠️**
- UI có button và popup
- Client gửi/nhận được messages
- Server broadcast DRAW_OFFER_NOTIFY
- ⚠️ Cần implement DRAW_ACCEPT handler (code mẫu ở trên)

Sau khi thêm DRAW_ACCEPT/DECLINE handlers là xong 100%! 🎉
