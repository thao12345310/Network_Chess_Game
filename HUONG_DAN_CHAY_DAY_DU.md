# Hướng Dẫn Chạy Network Chess Game (Linux)

## Tổng quan kiến trúc
```
┌─────────────┐         TCP Socket         ┌─────────────┐
│  Python UI  │ ◄────────────────────────► │ C++ Server  │
│  (Tkinter)  │                             │  (port 5001)│
└──────┬──────┘                             └─────────────┘
       │
       ├─ ctypes binding
       │
┌──────▼──────┐
│  C++ Client │
│ (shared lib)│
└─────────────┘
```

## Yêu cầu hệ thống

### Dependencies
```bash
# C++ compiler và build tools
sudo apt update
sudo apt install build-essential g++ make

# jsoncpp library (cho C++ client/server)
sudo apt install libjsoncpp-dev
sudo apt install nlohmann-json3-dev

# Python 3 và tkinter
sudo apt install python3 python3-tk

# Python packages cho server game logic
cd server/src/game_logic
pip3 install -r requirements.txt
```

## Bước 1: Build C++ Client (Shared Library)

```bash
cd client
make clean
make
make install  # Copy libchessclient.so sang folder ui/
```

**Output**: File `libchessclient.so` được tạo và copy vào `ui/`

**Kiểm tra**:
```bash
ls -l ui/libchessclient.so
# Phải thấy file tồn tại
```

## Bước 2: Build C++ Server

```bash
cd server/src
make clean
make
```

**Output**: File `server` executable

**Kiểm tra**:
```bash
./server --version  # Hoặc chỉ ./server để test
```

## Bước 3: Chạy Server

### Terminal 1 - Chạy Server
```bash
cd server/src
./server
```

**Bạn sẽ thấy**:
```
Server started on port 5001
Stream server listening on 127.0.0.1:5001
```

**Server đang chạy và lắng nghe trên port 5001**

## Bước 4: Chạy UI Client

### Terminal 2 - Chạy UI
```bash
cd ui
python3 app_main.py
```

**UI window sẽ mở ra với:**
1. Splash screen
2. Login screen
3. Connect button để kết nối server

## Hướng dẫn sử dụng

### 1. Kết nối Server
- Click **"Connect to Server"**
- Server mặc định: `127.0.0.1:5001`
- Nếu thành công, indicator chuyển sang màu xanh

### 2. Đăng ký / Đăng nhập
- **Register**: Điền username, password, email → Click "Register"
- **Login**: Điền username, password → Click "Login"

### 3. Lobby
- Sau khi login thành công, vào lobby screen
- Click **"Refresh Players"** để xem danh sách người chơi online
- Click **"Find Random Match"** để tìm đối thủ

### 4. Chơi game
- Khi match được tìm thấy, game screen sẽ mở
- Click vào quân cờ để chọn
- Click vào ô đích để di chuyển
- Các nút: Resign, Offer Draw, Chat

## Troubleshooting

### Lỗi: "C++ client library not found"
```bash
# Build lại C++ client
cd client
make clean
make
make install

# Kiểm tra file
ls -l ../ui/libchessclient.so
```

### Lỗi: "Connection refused"
```bash
# Kiểm tra server đang chạy
ps aux | grep server

# Kiểm tra port
netstat -tulpn | grep 5001

# Khởi động lại server
cd server/src
./server
```

### Lỗi compile C++: "jsoncpp not found"
```bash
# Cài jsoncpp
sudo apt install libjsoncpp-dev

# Hoặc build từ source
git clone https://github.com/open-source-parsers/jsoncpp.git
cd jsoncpp
mkdir build && cd build
cmake ..
make
sudo make install
```

### Lỗi Python: "No module named 'tkinter'"
```bash
sudo apt install python3-tk
```

### Server không compile
```bash
cd server/src
make clean

# Check dependencies
g++ --version
pkg-config --cflags --libs jsoncpp

# Build with verbose
make VERBOSE=1
```

## Chạy nhiều client cùng lúc

### Terminal 3 - Client 2
```bash
cd ui
python3 app_main.py
```

Mỗi client có thể:
- Login với username khác nhau
- Kết nối cùng server
- Chơi với nhau

## Kiến trúc Message Protocol

### Client → Server:
```json
{
    "messageType": "AUTH_LOGIN_REQ",
    "payload": {
        "username": "player1",
        "password": "pass123"
    }
}
```

### Server → Client:
```json
{
    "messageType": "AUTH_LOGIN_ACK",
    "responseCode": 200,
    "payload": {
        "user_id": 1,
        "elo": 1200
    }
}
```

Chi tiết protocol: Xem file `server/src/PROTOCOL_SPEC.json`

## Development Workflow

### Sửa C++ Client
```bash
cd client
# Sửa code trong src/
make clean
make
make install
# Restart UI để load library mới
```

### Sửa C++ Server
```bash
cd server/src
# Sửa code
make clean
make
# Ctrl+C để stop server cũ
./server
```

### Sửa Python UI
```bash
cd ui
# Sửa code trong các file screen_*.py
# Restart python app_main.py
```

## Quick Start Script

Tạo file `start_all.sh`:
```bash
#!/bin/bash

# Terminal 1: Server
gnome-terminal -- bash -c "cd server/src && ./server; exec bash"

# Wait for server to start
sleep 2

# Terminal 2: Client 1
gnome-terminal -- bash -c "cd ui && python3 app_main.py; exec bash"

# Terminal 3: Client 2 (optional)
gnome-terminal -- bash -c "cd ui && python3 app_main.py; exec bash"
```

Chạy:
```bash
chmod +x start_all.sh
./start_all.sh
```

## Logs và Debug

### Server logs
```bash
cd server/src
./server 2>&1 | tee server.log
```

### Client logs
```bash
cd ui
python3 app_main.py 2>&1 | tee client.log
```

### Network traffic
```bash
# Monitor port 5001
sudo tcpdump -i lo -A port 5001
```

## Testing

### Test C++ Client standalone
```bash
cd client
./chess_client
# Sẽ có menu để test các chức năng
```

### Test Server protocol
```bash
# Dùng netcat để test
nc localhost 5001

# Gửi message:
{"messageType":"AUTH_LOGIN_REQ","payload":{"username":"test","password":"test"}}
```

## Tài liệu tham khảo

- **Protocol Spec**: `server/src/PROTOCOL_SPEC.json`
- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Server Flow**: `server/src/STREAM_FLOW.md`

## Liên hệ / Báo lỗi

Nếu gặp vấn đề, kiểm tra:
1. Dependencies đã cài đủ chưa
2. Server đang chạy chưa
3. Shared library đã build chưa
4. Port 5001 có bị chiếm không

Chúc bạn chơi vui! ♟️
