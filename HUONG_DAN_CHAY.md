# Hướng dẫn chạy và thử chương trình

## Yêu cầu hệ thống

### Windows

- **Compiler**: MinGW-w64 hoặc Visual Studio (g++)
- **Python**: Python 3.x
- **Thư viện**:
  - `python-chess` (pip install python-chess)
  - `jsoncpp` (cho client, nếu dùng C++ client)

### Linux/WSL

- **Compiler**: g++ với C++11
- **Python**: python3
- **Thư viện**:
  - `python3-pip`
  - `python-chess` (pip3 install python-chess)
  - `libjsoncpp-dev` (cho client)

---

## Bước 1: Cài đặt dependencies

### Python dependencies

```bash
# Windows
pip install python-chess

# Linux/WSL
pip3 install python-chess
```

### Kiểm tra Python có sẵn

```bash
# Windows
python --version

# Linux/WSL
python3 --version
```

---

## Bước 2: Build Server

Có 3 cách chính, tùy bạn muốn đứng ở thư mục nào:

### Cách A – Build ngay trong `server/`

```bash
cd server
make            # hoặc: make run, make clean
```

Makefile này sẽ tự include `src/StreamServer.cpp` và `src/game_logic/*.cpp`.

### Cách B – Build trong `server/src/`

```bash
cd server/src
make
```

Tương tự cách A nhưng đặt Makefile gần hơn với code C++.

### Cách C – Build trực tiếp trong `server/src/game_logic/`

```bash
cd server/src/game_logic
make
```

Hoặc build thủ công:

```bash
# Windows
g++ -o server.exe main.cpp NetworkInterface.cpp ../StreamServer.cpp -I.. -lws2_32

# Linux/WSL
g++ -o server main.cpp NetworkInterface.cpp ../StreamServer.cpp -I.. -pthread
```

> 📌 **Mẹo**: Ngoài 3 Makefile trên, bạn có thể dùng script nhanh:
>
> - Windows: `run_server.bat`
> - Linux/WSL: `./run_server.sh` (nhớ `chmod +x` lần đầu)

---

## Bước 3: Chạy Server

### Khởi động server

```bash
# Windows
.\server.exe

# Linux/WSL
./server
```

Server sẽ lắng nghe trên `127.0.0.1:5001`

**Output mong đợi**:

```
Stream server listening on 127.0.0.1:5001
```

**Lưu ý**: Server chạy trong foreground, để dừng nhấn `Ctrl+C`

---

## Bước 4: Test Server

### Cách 1: Dùng Python test client (Khuyên dùng)

Mở terminal mới (giữ server đang chạy), vào thư mục server:

```bash
cd server/src/game_logic
python3 test_client.py
```

**Output mong đợi**:

```
Testing validate_move...
Response: {"status": "success", "is_valid": true, ...}
Testing calculate_elo...
Response: {"status": "success", "new_elo": 1216}
```

### Cách 2: Dùng C++ Client

#### Build Client

```bash
cd client
make
```

#### Chạy Client

```bash
# Windows
.\chess_client.exe

# Linux/WSL
./chess_client
```

### Cách 3: Test thủ công với telnet/netcat

**Windows (PowerShell)**:

```powershell
$client = New-Object System.Net.Sockets.TcpClient("127.0.0.1", 5001)
$stream = $client.GetStream()
$data = [System.Text.Encoding]::UTF8.GetBytes('{"action":"validate_move","fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1","move":"e2e4"}' + "`n")
$stream.Write($data, 0, $data.Length)
$buffer = New-Object byte[] 1024
$bytesRead = $stream.Read($buffer, 0, 1024)
[System.Text.Encoding]::UTF8.GetString($buffer, 0, $bytesRead)
$client.Close()
```

**Linux/WSL**:

```bash
echo '{"action":"validate_move","fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1","move":"e2e4"}' | nc 127.0.0.1 5001
```

---

## Bước 5: Test các API

### 1. Validate Move

```json
{
  "action": "validate_move",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move": "e2e4"
}
```

### 2. Calculate ELO

```json
{
  "action": "calculate_elo",
  "player_a_elo": 1200,
  "player_b_elo": 1200,
  "result_a": 1
}
```

### 3. Log Move

```json
{ "action": "log_move", "game_id": 1, "player_id": 1, "move": "e2e4" }
```

### 4. Get Replay

```json
{ "action": "get_replay", "game_id": 1 }
```

---

## Troubleshooting

### Lỗi: "Failed to create socket"

- **Nguyên nhân**: Port đã được sử dụng hoặc không có quyền
- **Giải pháp**:
  - Kiểm tra port 5001 có đang dùng: `netstat -an | findstr 5001` (Windows) hoặc `netstat -an | grep 5001` (Linux)
  - Đổi port trong `main.cpp` nếu cần

### Lỗi: "Bind failed"

- **Nguyên nhân**: Port đã được bind bởi process khác
- **Giải pháp**: Tắt process đang dùng port hoặc đổi port

### Lỗi: "Failed to open pipe" hoặc "python3: command not found"

- **Nguyên nhân**: Python không có trong PATH hoặc sai tên lệnh
- **Giải pháp**:
  - Windows: Sửa trong `NetworkInterface.cpp` dòng 33-35, đổi `python3` thành `python`
  - Linux: Đảm bảo `python3` có trong PATH

### Lỗi: "JSON parse error"

- **Nguyên nhân**: Format JSON không đúng hoặc thiếu newline
- **Giải pháp**: Đảm bảo mỗi message kết thúc bằng `\n`

### Lỗi compile: "StreamServer.h: No such file"

- **Nguyên nhân**: Đường dẫn include sai
- **Giải pháp**:
  - Copy `StreamServer.h` và `StreamServer.cpp` vào `server/src/game_logic/`
  - Hoặc sửa Makefile để include đúng đường dẫn

### Server không nhận được request

- **Kiểm tra**:
  1. Server đang chạy và in "Stream server listening..."
  2. Firewall không chặn port 5001
  3. Client kết nối đúng IP và port

---

## Chạy song song (Server + Test)

### Windows (PowerShell - 2 cửa sổ)

**Cửa sổ 1 - Server**:

```powershell
cd server\src\game_logic
.\server.exe
```

**Cửa sổ 2 - Test**:

```powershell
cd server\src\game_logic
python test_client.py
```

### Linux/WSL (2 terminal)

**Terminal 1 - Server**:

```bash
cd server/src/game_logic
./server
```

**Terminal 2 - Test**:

```bash
cd server/src/game_logic
python3 test_client.py
```

---

## Kiểm tra kết quả

### Server log

Server sẽ in ra:

```
Stream server listening on 127.0.0.1:5001
Received: {"action":"validate_move",...}
```

### Test client output

```
Testing validate_move...
Response: {"status": "success", "is_valid": true, "next_fen": "..."}

Testing calculate_elo...
Response: {"status": "success", "new_elo": 1216}
```

Nếu thấy output trên, chương trình đã chạy thành công! ✅
