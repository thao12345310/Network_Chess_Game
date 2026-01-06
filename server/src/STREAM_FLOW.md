# Sơ đồ Flow Stream Handling

## Tổng quan kiến trúc

```
┌─────────────┐                    ┌──────────────┐                    ┌─────────────┐
│   Client    │                    │   Server    │                    │ Game Logic  │
│             │                    │             │                    │   (Python)  │
└──────┬──────┘                    └──────┬──────┘                    └──────┬──────┘
       │                                    │                                  │
       │                                    │                                  │
       │  TCP Connection                    │                                  │
       │───────────────────────────────────>│                                  │
       │                                    │                                  │
       │                                    │                                  │
```

## Flow chi tiết - Gửi Request từ Client

### 1. Client Side (NetworkClient)

```
┌─────────────────────────────────────────────────────────────┐
│ NetworkClient::sendMessage(Json::Value)                     │
│                                                             │
│  1. Serialize JSON → string                                 │
│  2. Thêm delimiter "\n" vào cuối                            │
│  3. Gọi sendRaw(jsonStr)                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ NetworkClient::sendRaw(string)                              │
│                                                             │
│  Loop:                                                      │
│    - send(sockfd, data + offset, remaining, 0)             │
│    - Tích lũy totalSent                                     │
│    - Tiếp tục cho đến khi gửi hết                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ TCP Socket
                        │ (byte stream)
                        ▼
```

### 2. Server Side - StreamServer

```
                        │
                        │ TCP Socket
                        │ (byte stream)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ StreamServer::start()                                        │
│                                                             │
│  1. socket() → serverSocket                                 │
│  2. setsockopt(SO_REUSEADDR)                                │
│  3. bind(127.0.0.1:port)                                    │
│  4. listen(backlog=5)                                       │
│  5. Loop: accept() → spawn thread cho mỗi client             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ StreamServer::handleClient(SOCKET clientSocket)             │
│ [Chạy trong thread riêng cho mỗi client]                    │
│                                                             │
│  Loop:                                                      │
│    1. recv(clientSocket, buffer[4096], ...)                 │
│    2. buffer[bytesReceived] = '\0'                         │
│    3. Chuyển buffer → string request                        │
│    4. Tách theo newline (\n):                              │
│       - stringstream ss(request)                            │
│       - getline(ss, line) cho mỗi dòng                      │
│       - Loại bỏ '\r' nếu có                                 │
│    5. Với mỗi line (message):                               │
│       - Gọi handler(line) → response                        │
│       - send(response + "\n")                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ handler callback
                        ▼
```

### 3. Server Side - NetworkInterface

```
                        │
                        │ handler callback
                        │ (lambda: process_request)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ NetworkInterface::process_request(string request)           │
│                                                             │
│  1. Escape dấu " trong request                              │
│  2. Tạo command: "python logic_wrapper.py \"<request>\""    │
│  3. popen(command, "r") → pipe                              │
│  4. Đọc output từ pipe → result                             │
│  5. Trim whitespace đầu/cuối                                │
│  6. Return result (JSON string)                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ return response
                        ▼
```

### 4. Response Flow ngược lại

```
                        │
                        │ return response
                        │ (JSON string)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ StreamServer::handleClient()                                │
│                                                             │
│  - Nhận response từ handler                                 │
│  - send(clientSocket, response.c_str(), length, 0)          │
│  - send(clientSocket, "\n", 1, 0)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ TCP Socket
                        │ (byte stream)
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ NetworkClient::receiveRaw()                                 │
│                                                             │
│  Loop:                                                      │
│    - recv(sockfd, &ch, 1, 0) - đọc từng byte                │
│    - Nếu ch == '\n' → break                                 │
│    - Tích lũy vào buffer                                    │
│  Return: buffer (string không có \n)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ NetworkClient::receiveMessage()                             │
│                                                             │
│  1. Gọi receiveRaw() → string data                          │
│  2. Parse JSON từ data                                      │
│  3. Return Json::Value                                      │
└─────────────────────────────────────────────────────────────┘
```

## Sequence Diagram

```
Client              StreamServer          NetworkInterface      Python Logic
  │                      │                        │                  │
  │──connect()──────────>│                        │                  │
  │                      │──accept()──────────────│                  │
  │                      │──spawn thread──────────>│                  │
  │                      │                        │                  │
  │──send(JSON + \n)────>│                        │                  │
  │                      │──recv(buffer)──────────│                  │
  │                      │──getline()─────────────│                  │
  │                      │──handler(line)─────────>│                  │
  │                      │                        │──popen()─────────>│
  │                      │                        │                  │──process
  │                      │                        │<──result─────────│
  │                      │<──return(response)─────│                  │
  │                      │──send(response + \n)───│                  │
  │<──recv(response)─────│                        │                  │
  │──parse JSON──────────│                        │                  │
```

## Message Framing Protocol

- **Delimiter**: Newline character (`\n`)
- **Format**: Mỗi message là một dòng JSON, kết thúc bằng `\n`
- **Encoding**: UTF-8 string
- **Max message size**: Không giới hạn (cần cải thiện)

## Buffer Handling

### Client (receiveRaw)
- Đọc từng byte cho đến khi gặp `\n`
- Timeout: 5 giây (SO_RCVTIMEO)
- Nếu timeout → return empty string

### Server (handleClient)
- Buffer size: 4096 bytes
- Nếu một message > 4096 bytes → có thể bị cắt
- **Vấn đề**: Không có buffer tích lũy giữa các lần recv()

## Threading Model

```
Main Thread
  └── StreamServer::start()
       └── Loop: accept()
            ├── Thread 1: handleClient(client1)
            ├── Thread 2: handleClient(client2)
            └── Thread N: handleClient(clientN)
```

Mỗi client có một thread riêng, xử lý độc lập.

## Error Handling

### Client
- `send()` fail → set `connected = false`
- `recv()` timeout → return empty (không phải lỗi)
- `recv()` = 0 → connection closed
- JSON parse error → return empty Json::Value

### Server
- `recv()` <= 0 → break loop, close socket
- `handler()` return empty → gửi error JSON
- `popen()` fail → return error JSON

## Các điểm cần cải thiện

1. **Buffer tích lũy**: Server cần buffer để xử lý message bị cắt giữa các lần recv()
2. **Message size limit**: Cần giới hạn kích thước message để tránh DoS
3. **Keep-alive**: Thêm heartbeat để phát hiện connection die
4. **Thread pool**: Thay vì spawn thread mới, dùng thread pool
5. **Graceful shutdown**: Cần cơ chế dừng server an toàn

