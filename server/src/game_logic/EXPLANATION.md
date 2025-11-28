# Giải thích chi tiết: Game Logic + Network Interface

## 📋 Tổng quan kiến trúc

Hệ thống sử dụng kiến trúc **hybrid C++/Python**:
- **C++ (NetworkInterface)**: Xử lý TCP socket connections, nhận và gửi requests
- **Python (game_logic)**: Xử lý logic cờ vua, tính toán ELO, tương tác database

---

## 🔄 Luồng code chi tiết

### 1. Khởi động Server (`main.cpp`)

```
main.cpp → NetworkInterface(5001) → server.start()
```

**File: `main.cpp`**
```cpp
NetworkInterface server(5001);  // Tạo server lắng nghe port 5001
server.start();                  // Bắt đầu lắng nghe connections
```

**Chức năng:**
- Khởi tạo NetworkInterface với port 5001
- Bắt đầu server để lắng nghe các kết nối TCP

---

### 2. NetworkInterface - Lắng nghe Connections

**File: `NetworkInterface.cpp` → `start()`**

**Luồng hoạt động:**

```
1. Tạo socket (AF_INET, SOCK_STREAM)
   ↓
2. Bind socket đến 127.0.0.1:5001
   ↓
3. Listen với backlog = 5
   ↓
4. Vòng lặp chính:
   ├─ accept() nhận client connection
   ├─ Tạo thread mới cho mỗi client
   └─ handle_client() xử lý client trong thread riêng
```

**Chi tiết code:**

**a) Khởi tạo socket và bind:**
```cpp
server_socket = socket(AF_INET, SOCK_STREAM, 0);  // Tạo TCP socket
setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, ...);  // Cho phép tái sử dụng address

sockaddr_in server_addr;
server_addr.sin_family = AF_INET;
server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");  // Localhost
server_addr.sin_port = htons(5001);  // Port 5001

bind(server_socket, ...);  // Gắn socket với address
listen(server_socket, 5);  // Bắt đầu lắng nghe, tối đa 5 pending connections
```

**b) Vòng lặp chấp nhận clients:**
```cpp
while (running) {
    SOCKET client_socket = accept(server_socket, NULL, NULL);
    // Mỗi client được xử lý trong thread riêng
    std::thread client_thread(&NetworkInterface::handle_client, this, client_socket);
    client_thread.detach();  // Thread tự giải phóng khi xong
}
```

---

### 3. Xử lý Client Request (`handle_client()`)

**File: `NetworkInterface.cpp` → `handle_client(SOCKET client_socket)`**

**Luồng:**

```
1. Nhận data từ client qua recv()
   ↓
2. Parse từng dòng (mỗi dòng = 1 JSON request)
   ↓
3. Với mỗi dòng:
   ├─ process_request(line) → xử lý request
   ├─ Gửi response về client
   └─ Lặp lại
```

**Chi tiết:**

```cpp
char buffer[4096];
while (true) {
    int bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
    if (bytes_received <= 0) break;  // Client disconnect
    
    buffer[bytes_received] = '\0';
    std::string request(buffer);
    
    // Parse từng dòng (vì có thể nhận nhiều requests cùng lúc)
    std::stringstream ss(request);
    std::string line;
    while (std::getline(ss, line)) {
        if (line.empty()) continue;
        
        // Xử lý request
        std::string response = process_request(line);
        
        // Gửi response về client
        send(client_socket, response.c_str(), response.length(), 0);
        send(client_socket, "\n", 1, 0);  // Thêm newline
    }
}
```

**Đặc điểm:**
- Mỗi client được xử lý trong thread riêng → hỗ trợ nhiều client đồng thời
- Hỗ trợ nhận nhiều requests trong 1 buffer (parse theo dòng)
- Response được gửi ngay sau khi xử lý xong

---

### 4. Xử lý Request → Gọi Python Logic (`process_request()`)

**File: `NetworkInterface.cpp` → `process_request(const std::string& request)`**

**Luồng quan trọng nhất:**

```
1. Nhận JSON request string từ client
   ↓
2. Escape các ký tự đặc biệt (dấu ngoặc kép)
   ↓
3. Tạo command: python logic_wrapper.py "<escaped_json>"
   ↓
4. Chạy command qua popen/_popen (pipe)
   ↓
5. Đọc output từ Python script
   ↓
6. Trả về JSON response cho client
```

**Chi tiết code:**

```cpp
std::string NetworkInterface::process_request(const std::string& request) {
    // 1. Escape dấu ngoặc kép để truyền qua command line an toàn
    std::string escaped_request;
    for (char c : request) {
        if (c == '"') {
            escaped_request += "\\\"";
        } else {
            escaped_request += c;
        }
    }
    
    // 2. Tạo command để gọi Python script
    std::string command = "python logic_wrapper.py \"" + escaped_request + "\"";
    // Windows: "python logic_wrapper.py ..."
    // Linux:   "python3 logic_wrapper.py ..."
    
    // 3. Chạy command và đọc output
    FILE* pipe = popen(command.c_str(), "r");
    
    std::string result = "";
    char buffer[128];
    while (fgets(buffer, 128, pipe) != NULL) {
        result += buffer;  // Đọc tất cả output từ Python
    }
    
    pclose(pipe);
    
    // 4. Trim whitespace và trả về
    // ... (trim logic)
    
    return result;  // JSON response từ Python
}
```

**Cách hoạt động:**
- C++ server gọi Python script qua system pipe
- Python script xử lý logic và in JSON ra stdout
- C++ đọc stdout và trả về cho client
- **Lưu ý:** Mỗi request tạo 1 process Python mới (có thể tối ưu sau)

---

### 5. Python Logic Wrapper (`logic_wrapper.py`)

**File: `logic_wrapper.py` → `main()`**

**Luồng:**

```
1. Đọc JSON input từ command line argument
   ↓
2. Parse JSON: req = json.loads(input_str)
   ↓
3. Kiểm tra action type:
   ├─ "validate_move" → gọi validate_move()
   ├─ "calculate_elo" → gọi calculate_elo()
   ├─ "game_result" → gọi determine_result()
   ├─ "log_move" → gọi insert_move()
   ├─ "get_replay" → gọi get_moves()
   └─ "update_elo", "update_game_result" → các DB operations
   ↓
4. Tạo JSON response
   ↓
5. In ra stdout (C++ sẽ đọc)
```

**Chi tiết:**

```python
def main():
    # Đọc input từ command line argument
    input_str = " ".join(sys.argv[1:])  # Lấy từ sys.argv[1]
    req = json.loads(input_str)         # Parse JSON
    
    action = req.get('action')
    
    if action == 'validate_move':
        fen = req.get('fen')
        move = req.get('move')
        is_valid, next_fen = validate_move(fen, move)
        response = {"status": "success", "is_valid": is_valid, "next_fen": next_fen}
    
    elif action == 'calculate_elo':
        p_a = req.get('player_a_elo')
        p_b = req.get('player_b_elo')
        res_a = req.get('result_a')
        new_elo = calculate_elo(p_a, p_b, res_a)
        response = {"status": "success", "new_elo": new_elo}
    
    # ... các actions khác
    
    print(json.dumps(response))  # In JSON ra stdout
```

**Các actions được hỗ trợ:**

| Action | Mô tả | Input | Output |
|--------|-------|-------|--------|
| `validate_move` | Kiểm tra nước đi hợp lệ | `fen`, `move` | `is_valid`, `next_fen` |
| `game_result` | Xác định kết quả game | `fen` | `result` (checkmate/draw/in_progress) |
| `calculate_elo` | Tính ELO mới sau game | `player_a_elo`, `player_b_elo`, `result_a` | `new_elo` |
| `log_move` | Lưu nước đi vào DB | `game_id`, `player_id`, `move` | `status` |
| `get_replay` | Lấy danh sách nước đi | `game_id` | `moves` (array) |
| `update_elo` | Cập nhật ELO player | `player_id`, `new_elo` | `status` |
| `update_game_result` | Cập nhật kết quả game | `game_id`, `winner_id`, `status`, `end_time` | `status` |

---

### 6. Game Logic Module (`game_logic.py`)

**File: `game_logic.py`**

**a) `validate_move(fen, move_uci)`:**
```python
def validate_move(fen, move_uci):
    board = chess.Board(fen)                    # Tạo board từ FEN string
    move = chess.Move.from_uci(move_uci)        # Parse UCI move (e.g., "e2e4")
    if move in board.legal_moves:               # Kiểm tra hợp lệ
        board.push(move)                        # Thực hiện nước đi
        return True, board.fen()                # Trả về True + FEN mới
    else:
        return False, fen                       # Trả về False + FEN cũ
```

**Chức năng:**
- Nhận FEN string (trạng thái bàn cờ) và nước đi dạng UCI
- Sử dụng thư viện `python-chess` để validate
- Trả về `(is_valid, next_fen)`

**b) `determine_result(fen)`:**
```python
def determine_result(fen):
    board = chess.Board(fen)
    if board.is_checkmate():        # Chiếu hết
        return "checkmate"
    elif board.is_stalemate():      # Hết nước đi (hòa)
        return "draw"
    elif board.is_insufficient_material():  # Không đủ quân (hòa)
        return "draw"
    elif board.is_seventyfive_moves():      # 75 nước không bắt quân (hòa)
        return "draw"
    else:
        return "in_progress"        # Game đang tiếp tục
```

**Chức năng:**
- Kiểm tra trạng thái kết thúc của game từ FEN
- Trả về: `"checkmate"`, `"draw"`, hoặc `"in_progress"`

---

### 7. ELO System (`elo_system.py`)

**File: `elo_system.py`**

```python
def calculate_elo(player_a, player_b, result_a, k=32):
    """
    result_a: 1 = win, 0.5 = draw, 0 = lose
    """
    expected_a = 1 / (1 + 10 ** ((player_b - player_a) / 400))
    new_a = player_a + k * (result_a - expected_a)
    return round(new_a)
```

**Công thức ELO:**
- **Expected score:** `E_A = 1 / (1 + 10^((R_B - R_A) / 400))`
- **New rating:** `R_A_new = R_A + K * (S_A - E_A)`
  - `S_A`: Kết quả thực tế (1=thắng, 0.5=hòa, 0=thua)
  - `K`: Hệ số K-factor (mặc định 32)
  - `E_A`: Điểm kỳ vọng

**Ví dụ:**
- Player A: 1200 ELO, Player B: 1200 ELO
- Player A thắng (`result_a = 1`)
- Expected: `E_A = 0.5` (50% cơ hội)
- New ELO: `1200 + 32 * (1 - 0.5) = 1216`

---

### 8. Database Handler (`db_handler.py`)

**File: `db_handler.py`**

Các hàm tương tác với SQLite database:

**a) `insert_move(game_id, player_id, move_notation)`:**
- Lưu nước đi vào bảng `Move`

**b) `get_moves(game_id)`:**
- Lấy tất cả nước đi của game (để replay)

**c) `update_player_elo(player_id, new_elo)`:**
- Cập nhật ELO của player

**d) `update_game_result(game_id, winner_id, status, end_time)`:**
- Cập nhật kết quả game khi kết thúc

**Chi tiết:**
```python
def insert_move(game_id, player_id, move_notation):
    conn = get_connection()  # Kết nối SQLite
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Move (game_id, player_id, move_notation) VALUES (?, ?, ?)",
        (game_id, player_id, move_notation)
    )
    conn.commit()
    conn.close()
```

---

## 🧪 Giải thích các Test trong `test_client.py`

### Tổng quan

File `test_client.py` là một **test client** đơn giản để kiểm tra server hoạt động đúng. Nó kết nối đến server và gửi 2 test requests.

---

### Test 1: Validate Move

```python
# Test 1: Validate Move
print("Testing validate_move...")
req = {
    "action": "validate_move",
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "move": "e2e4"
}
s.sendall((json.dumps(req) + "\n").encode('utf-8'))
resp = f.readline()
print(f"Response: {resp.strip()}")
```

**Mục đích:**
- Kiểm tra chức năng validate nước đi có hoạt động đúng không

**Chi tiết:**
1. **FEN string**: `"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"`
   - Đây là **bàn cờ khởi đầu** (starting position)
   - `rnbqkbnr`: Hàng 8 (quân đen)
   - `pppppppp`: Hàng 7 (tốt đen)
   - `8`: 8 ô trống
   - `PPPPPPPP`: Hàng 2 (tốt trắng)
   - `RNBQKBNR`: Hàng 1 (quân trắng)
   - `w`: Lượt trắng đi
   - `KQkq`: Quyền nhập thành
   - `-`: Không có en passant
   - `0 1`: Halfmove và fullmove counter

2. **Move**: `"e2e4"`
   - Nước đi: tốt trắng từ e2 → e4 (nước đi mở phổ biến)
   - Đây là nước đi **hợp lệ** ở vị trí khởi đầu

3. **Luồng xử lý:**
   ```
   Client → NetworkInterface → logic_wrapper.py → game_logic.validate_move()
   ↓
   Kiểm tra move "e2e4" có hợp lệ không?
   ↓
   True (hợp lệ)
   ↓
   Thực hiện nước đi, tạo FEN mới
   ↓
   Response: {"status": "success", "is_valid": true, "next_fen": "..."}
   ```

4. **Kết quả mong đợi:**
   ```json
   {
     "status": "success",
     "is_valid": true,
     "next_fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
   }
   ```
   - `is_valid: true` → nước đi hợp lệ
   - `next_fen` → FEN string sau khi thực hiện nước đi

---

### Test 2: Calculate ELO

```python
# Test 2: Calculate ELO
print("\nTesting calculate_elo...")
req = {
    "action": "calculate_elo",
    "player_a_elo": 1200,
    "player_b_elo": 1200,
    "result_a": 1
}
s.sendall((json.dumps(req) + "\n").encode('utf-8'))
resp = f.readline()
print(f"Response: {resp.strip()}")
```

**Mục đích:**
- Kiểm tra chức năng tính toán ELO có hoạt động đúng không

**Chi tiết:**
1. **Input:**
   - `player_a_elo: 1200` → ELO ban đầu của player A
   - `player_b_elo: 1200` → ELO ban đầu của player B
   - `result_a: 1` → Player A thắng (1=win, 0.5=draw, 0=lose)

2. **Tính toán:**
   ```
   Expected_A = 1 / (1 + 10^((1200-1200)/400))
                = 1 / (1 + 10^0)
                = 1 / 2
                = 0.5
   
   New_ELO_A = 1200 + 32 * (1 - 0.5)
             = 1200 + 32 * 0.5
             = 1200 + 16
             = 1216
   ```

3. **Luồng xử lý:**
   ```
   Client → NetworkInterface → logic_wrapper.py → elo_system.calculate_elo()
   ↓
   Tính toán ELO mới theo công thức
   ↓
   Response: {"status": "success", "new_elo": 1216}
   ```

4. **Kết quả mong đợi:**
   ```json
   {
     "status": "success",
     "new_elo": 1216
   }
   ```
   - `new_elo: 1216` → ELO mới của player A sau khi thắng

---

### Cấu trúc Test Client

```python
def test_client():
    time.sleep(1)  # Đợi 1 giây để server khởi động xong
    
    try:
        # 1. Tạo socket và kết nối
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5001))  # Kết nối đến localhost:5001
        f = s.makefile('r', encoding='utf-8')  # Tạo file-like object để đọc dòng
        
        # 2. Chạy Test 1: Validate Move
        # ... (đã giải thích ở trên)
        
        # 3. Đợi 0.5 giây
        time.sleep(0.5)
        
        # 4. Chạy Test 2: Calculate ELO
        # ... (đã giải thích ở trên)
        
        # 5. Đóng kết nối
        s.close()
        
    except Exception as e:
        print(f"Test failed: {e}")
```

**Đặc điểm:**
- **Blocking I/O**: Chờ response từ server bằng `f.readline()`
- **Sequential**: Chạy từng test một, không parallel
- **Simple**: Chỉ test 2 chức năng cơ bản nhất

---

## 📊 Sơ đồ luồng tổng thể

```
┌─────────────┐
│   Client    │  (test_client.py hoặc game client)
│             │
└──────┬──────┘
       │ JSON request qua TCP socket
       ▼
┌─────────────────────────────────────┐
│   NetworkInterface (C++)            │
│   - Socket server (port 5001)       │
│   - handle_client() (multi-thread)  │
│   - process_request()               │
└──────┬──────────────────────────────┘
       │ Gọi Python qua popen()
       ▼
┌─────────────────────────────────────┐
│   logic_wrapper.py                  │
│   - Parse JSON input                │
│   - Route đến các functions         │
└──────┬──────────────────────────────┘
       │
       ├─→ game_logic.py
       │   ├─ validate_move()     (python-chess)
       │   └─ determine_result()  (python-chess)
       │
       ├─→ elo_system.py
       │   └─ calculate_elo()     (công thức ELO)
       │
       └─→ db_handler.py
           ├─ insert_move()       (SQLite)
           ├─ get_moves()         (SQLite)
           ├─ update_player_elo() (SQLite)
           └─ update_game_result()(SQLite)
```

---

## 🔍 Điểm quan trọng cần lưu ý

1. **Kiến trúc Hybrid:**
   - C++ xử lý network (hiệu năng tốt)
   - Python xử lý logic (dễ maintain, có thư viện chess tốt)

2. **Inter-process Communication:**
   - C++ gọi Python qua `popen()` → tạo process mới mỗi request
   - Communication qua stdin/stdout (JSON)

3. **Multi-threading:**
   - Mỗi client được xử lý trong thread riêng
   - Có thể xử lý nhiều clients đồng thời

4. **Error Handling:**
   - Tất cả errors được trả về dạng JSON với `"status": "error"`
   - Client cần check status trước khi dùng data

5. **Protocol:**
   - Request: JSON string + `\n` (newline)
   - Response: JSON string + `\n` (newline)
   - Mỗi dòng = 1 request/response

---

## 🎯 Tóm tắt

**Luồng chính:**
1. Client kết nối TCP đến port 5001
2. NetworkInterface nhận request, tạo thread xử lý
3. Mỗi request được gửi đến Python script qua popen
4. Python xử lý logic và trả JSON response
5. Response được gửi về client

**Test Client:**
- Test 1: Kiểm tra validate nước đi (e2e4 từ starting position)
- Test 2: Kiểm tra tính toán ELO (1200 → 1216 khi thắng)

**Ưu điểm:**
- Tách biệt network và logic
- Dễ test và maintain
- Có thể scale (multi-thread)

**Nhược điểm:**
- Mỗi request tạo process Python mới (có thể tối ưu bằng persistent Python process)
- Cần cài đặt cả C++ và Python dependencies

