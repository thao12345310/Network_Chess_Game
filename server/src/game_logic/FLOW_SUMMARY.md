# Tóm tắt luồng code - Game Logic + Network Interface

## 🔄 Luồng request nhanh (Quick Flow)

```
CLIENT
  │
  │ [1] Kết nối TCP đến 127.0.0.1:5001
  │
  ▼
┌─────────────────────────────────────┐
│ NetworkInterface (C++)              │
│ - main.cpp: khởi động server        │
│ - start(): lắng nghe port 5001      │
│ - handle_client(): nhận request     │
│ - process_request(): gọi Python     │
└─────────────────────────────────────┘
  │
  │ [2] popen("python logic_wrapper.py <json>")
  │
  ▼
┌─────────────────────────────────────┐
│ logic_wrapper.py                    │
│ - Đọc JSON từ command line          │
│ - Phân loại action:                 │
│   • validate_move → game_logic.py   │
│   • calculate_elo → elo_system.py   │
│   • log_move → db_handler.py        │
│ - In JSON response ra stdout        │
└─────────────────────────────────────┘
  │
  │ [3] JSON response qua stdout
  │
  ▼
┌─────────────────────────────────────┐
│ NetworkInterface (C++)              │
│ - Đọc stdout từ Python process      │
│ - Gửi response về client qua socket │
└─────────────────────────────────────┘
  │
  │ [4] JSON response
  │
  ▼
CLIENT nhận response
```

---

## 📝 Các Test trong test_client.py

### Test 1: Validate Move
**Mục đích:** Kiểm tra server có validate nước đi đúng không

**Request:**
```json
{
  "action": "validate_move",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move": "e2e4"
}
```
- FEN: bàn cờ khởi đầu (starting position)
- Move: tốt trắng từ e2 → e4

**Expected Response:**
```json
{
  "status": "success",
  "is_valid": true,
  "next_fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
}
```

---

### Test 2: Calculate ELO
**Mục đích:** Kiểm tra tính toán ELO có đúng không

**Request:**
```json
{
  "action": "calculate_elo",
  "player_a_elo": 1200,
  "player_b_elo": 1200,
  "result_a": 1
}
```
- Cả 2 player có ELO 1200
- Player A thắng (result_a = 1)

**Expected Response:**
```json
{
  "status": "success",
  "new_elo": 1216
}
```
- ELO mới: 1200 + 32*(1-0.5) = 1216

---

## 🔑 Các Actions được hỗ trợ

| Action | Module | Mô tả |
|--------|--------|-------|
| `validate_move` | game_logic.py | Kiểm tra nước đi hợp lệ |
| `game_result` | game_logic.py | Xác định kết quả game |
| `calculate_elo` | elo_system.py | Tính ELO mới |
| `log_move` | db_handler.py | Lưu nước đi vào DB |
| `get_replay` | db_handler.py | Lấy danh sách nước đi |
| `update_elo` | db_handler.py | Cập nhật ELO player |
| `update_game_result` | db_handler.py | Cập nhật kết quả game |

---

## 📦 Các module chính

1. **NetworkInterface.cpp/h**
   - Xử lý TCP socket
   - Multi-thread client handling
   - Giao tiếp với Python qua popen

2. **logic_wrapper.py**
   - Router/Dispatcher
   - Parse JSON và route đến các modules

3. **game_logic.py**
   - validate_move(): kiểm tra nước đi
   - determine_result(): xác định kết quả

4. **elo_system.py**
   - calculate_elo(): công thức ELO rating

5. **db_handler.py**
   - CRUD operations cho database
   - insert_move(), get_moves(), update_elo(), etc.

6. **database.py**
   - Connection helper cho SQLite

---

## ⚡ Đặc điểm quan trọng

- **Multi-threaded**: Mỗi client có thread riêng
- **Hybrid architecture**: C++ (network) + Python (logic)
- **IPC qua popen**: Mỗi request tạo Python process mới
- **Protocol**: JSON qua TCP socket, mỗi dòng = 1 request

