# Game Logic + Network Interface (Hybrid Architecture)

## Kiến trúc
- **C++ Server**: Xử lý TCP sockets (đáp ứng yêu cầu sử dụng C/C++ cho network)
- **Python Logic**: Xử lý game rules, database, ELO qua `logic_wrapper.py`

## Luồng hoạt động
1. **Server (`server.exe`)**: Lắng nghe trên `127.0.0.1:5001`
2. **Client gửi request**: JSON string kết thúc bằng newline
3. **Xử lý**: Server gọi `python3 logic_wrapper.py <json>` qua `popen`
4. **Response**: Server trả kết quả JSON về client

## Cài đặt và chạy

### 1. Cài đặt dependencies
**Linux/WSL**:
```bash
sudo apt update
sudo apt install python3-pip -y
pip3 install python-chess
```

**Windows**:
```bash
pip install python-chess
```

### 2. Build server
**Windows**:
```bash
g++ -o server main.cpp NetworkInterface.cpp -lws2_32
```

**Linux/WSL**:
```bash
make
# hoặc:
g++ -o server main.cpp NetworkInterface.cpp -pthread
```

### 3. Chạy server
```bash
./server      # Linux/WSL
./server.exe  # Windows
```

### 4. Test
```bash
python3 test_client.py
```

## API Protocol

Client gửi JSON qua socket:
```json
{"action": "validate_move", "fen": "...", "move": "e2e4"}
{"action": "calculate_elo", "player_a_elo": 1200, "player_b_elo": 1200, "result_a": 1}
{"action": "log_move", "game_id": 1, "player_id": 1, "move": "e2e4"}
{"action": "get_replay", "game_id": 1}
```

Server trả về:
```json
{"status": "success", "is_valid": true, "next_fen": "..."}
{"status": "success", "new_elo": 1216}
```