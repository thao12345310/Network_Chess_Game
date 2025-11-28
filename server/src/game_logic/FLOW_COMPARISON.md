# So sánh Flow: Kiến trúc Cũ vs Mới (với StreamServer)

## 📊 Tổng quan thay đổi

### Kiến trúc Cũ:
```
NetworkInterface
├─ Socket management (tự quản lý)
├─ Accept clients (tự quản lý)
├─ handle_client() (xử lý stream)
└─ process_request() (gọi Python)
```

### Kiến trúc Mới:
```
NetworkInterface
├─ StreamServer (delegation)
│  ├─ Socket management
│  ├─ Accept clients
│  └─ handleClient() (xử lý stream)
└─ process_request() (gọi Python)
```

**Điểm khác biệt chính:** Tách biệt **Stream Handling** ra thành lớp `StreamServer` riêng

---

## 🔄 Flow chi tiết - So sánh

### **FLOW CŨ** (theo FLOW_SUMMARY.md):

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Khởi động (main.cpp)                                     │
└─────────────────────────────────────────────────────────────┘
  │
  │ NetworkInterface(5001)
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. NetworkInterface::start()                                │
│    - Tạo socket                                             │
│    - Bind 127.0.0.1:5001                                    │
│    - Listen                                                 │
│    - Loop: accept() → handle_client() (thread)              │
└─────────────────────────────────────────────────────────────┘
  │
  │ Client connect
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. NetworkInterface::handle_client()                        │
│    - recv() nhận data                                       │
│    - Parse theo dòng                                        │
│    - Gọi process_request()                                  │
│    - send() response                                        │
└─────────────────────────────────────────────────────────────┘
  │
  │ process_request(line)
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. NetworkInterface::process_request()                      │
│    - Escape JSON                                            │
│    - popen("python logic_wrapper.py ...")                   │
│    - Đọc stdout từ Python                                   │
│    - Return response                                        │
└─────────────────────────────────────────────────────────────┘
  │
  │ popen() → Python process
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. logic_wrapper.py                                         │
│    - Parse JSON                                             │
│    - Route actions                                          │
│    - Print JSON response                                    │
└─────────────────────────────────────────────────────────────┘
  │
  │ stdout → pipe → C++
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Return response về handle_client()                       │
│    - send() về client                                       │
└─────────────────────────────────────────────────────────────┘
```

---

### **FLOW MỚI** (với StreamServer):

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Khởi động (main.cpp)                                     │
└─────────────────────────────────────────────────────────────┘
  │
  │ NetworkInterface(5001)
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. NetworkInterface Constructor                             │
│    - Tạo StreamServer với callback:                         │
│      [this](const std::string &request) {                   │
│          return process_request(request);                    │
│      }                                                       │
│    - Lambda capture 'this' để gọi NetworkInterface          │
└─────────────────────────────────────────────────────────────┘
  │
  │ streamServer = make_unique<StreamServer>(port, handler)
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. NetworkInterface::start()                                │
│    - Chỉ delegate: streamServer->start()                    │
│    - Không tự quản lý socket                                │
└─────────────────────────────────────────────────────────────┘
  │
  │ streamServer->start()
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. StreamServer::start()                                    │
│    - Tạo socket                                             │
│    - Bind 127.0.0.1:5001                                    │
│    - Listen                                                 │
│    - Loop: accept() → handleClient() (thread)               │
└─────────────────────────────────────────────────────────────┘
  │
  │ Client connect
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. StreamServer::handleClient()                             │
│    - recv() nhận data                                       │
│    - Parse theo dòng                                        │
│    - Gọi handler callback (chính là                         │
│      NetworkInterface::process_request())                   │
│    - send() response                                        │
└─────────────────────────────────────────────────────────────┘
  │
  │ handler(line) → process_request()
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. NetworkInterface::process_request()                      │
│    - Escape JSON                                            │
│    - popen("python logic_wrapper.py ...")                   │
│    - Đọc stdout từ Python                                   │
│    - Return response                                        │
└─────────────────────────────────────────────────────────────┘
  │
  │ popen() → Python process
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. logic_wrapper.py                                         │
│    - Parse JSON                                             │
│    - Route actions                                          │
│    - Print JSON response                                    │
└─────────────────────────────────────────────────────────────┘
  │
  │ stdout → pipe → C++
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. Return response về handleClient()                        │
│    - send() về client                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 So sánh chi tiết từng bước

### Bước 1: Khởi động Server

**CŨ:**
```cpp
// main.cpp
NetworkInterface server(5001);
server.start();
```

**MỚI:**
```cpp
// main.cpp (giống nhau)
NetworkInterface server(5001);
server.start();
```

**Khác biệt:** Không thay đổi ở main.cpp

---

### Bước 2: Constructor

**CŨ:**
```cpp
// NetworkInterface.cpp
NetworkInterface::NetworkInterface(int port) 
    : port(port), running(false), server_socket(INVALID_SOCKET) {
    // Chỉ khởi tạo biến
}
```

**MỚI:**
```cpp
// NetworkInterface.cpp
NetworkInterface::NetworkInterface(int port) : port(port) {
    streamServer = std::make_unique<StreamServer>(
        port, 
        [this](const std::string &request) { 
            return process_request(request); 
        }
    );
}
```

**Khác biệt:**
- ✅ Tạo StreamServer ngay trong constructor
- ✅ Truyền callback function (lambda) để StreamServer gọi lại
- ✅ Sử dụng `std::unique_ptr` để quản lý memory

---

### Bước 3: Start Server

**CŨ:**
```cpp
// NetworkInterface.cpp
void NetworkInterface::start() {
    // Tự tạo socket
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    // Tự bind
    bind(server_socket, ...);
    // Tự listen
    listen(server_socket, 5);
    
    // Loop accept
    while (running) {
        SOCKET client_socket = accept(...);
        std::thread client_thread(&NetworkInterface::handle_client, this, client_socket);
        client_thread.detach();
    }
}
```

**MỚI:**
```cpp
// NetworkInterface.cpp
void NetworkInterface::start() {
    if (!streamServer) {
        std::cerr << "Stream server is not initialized" << std::endl;
        return;
    }
    streamServer->start();  // Chỉ delegate
}

// StreamServer.cpp
void StreamServer::start() {
    // Tạo socket
    serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    // Bind
    bind(serverSocket, ...);
    // Listen
    listen(serverSocket, 5);
    
    // Loop accept
    while (running) {
        SOCKET clientSocket = accept(...);
        std::thread clientThread(&StreamServer::handleClient, this, clientSocket);
        clientThread.detach();
    }
}
```

**Khác biệt:**
- ✅ NetworkInterface không còn tự quản lý socket
- ✅ Tất cả socket logic chuyển sang StreamServer
- ✅ NetworkInterface chỉ delegate → separation of concerns

---

### Bước 4: Handle Client Connection

**CŨ:**
```cpp
// NetworkInterface.cpp
void NetworkInterface::handle_client(SOCKET client_socket) {
    char buffer[4096];
    while (true) {
        int bytes_received = recv(client_socket, buffer, ...);
        if (bytes_received <= 0) break;
        
        // Parse lines
        std::stringstream ss(request);
        std::string line;
        while (std::getline(ss, line)) {
            // Gọi process_request trực tiếp
            std::string response = process_request(line);
            send(client_socket, response.c_str(), ...);
        }
    }
}
```

**MỚI:**
```cpp
// StreamServer.cpp
void StreamServer::handleClient(SOCKET clientSocket) {
    char buffer[4096];
    while (true) {
        int bytesReceived = recv(clientSocket, buffer, ...);
        if (bytesReceived <= 0) break;
        
        // Parse lines
        std::stringstream ss(request);
        std::string line;
        while (std::getline(ss, line)) {
            // Gọi handler callback (là process_request)
            std::string response = handler ? handler(line) : "";
            send(clientSocket, response.c_str(), ...);
        }
    }
}

// NetworkInterface.cpp
// process_request() không thay đổi
```

**Khác biệt:**
- ✅ `handle_client` chuyển sang `StreamServer::handleClient`
- ✅ Gọi handler callback thay vì gọi trực tiếp
- ✅ NetworkInterface::process_request() không đổi
- ✅ StreamServer không biết về NetworkInterface, chỉ biết về handler function

---

### Bước 5: Process Request

**CŨ và MỚI:** Giống nhau hoàn toàn
```cpp
// NetworkInterface.cpp
std::string NetworkInterface::process_request(const std::string& request) {
    // Escape JSON
    // popen("python logic_wrapper.py ...")
    // Đọc stdout
    // Return response
}
```

**Khác biệt:** Không có

---

## 📋 Tổng hợp thay đổi

### Code Organization:

| Aspect | Cũ | Mới |
|--------|----|----|
| **Socket Management** | NetworkInterface | StreamServer |
| **Accept Loop** | NetworkInterface | StreamServer |
| **Stream Handling** | NetworkInterface::handle_client() | StreamServer::handleClient() |
| **Request Processing** | NetworkInterface::process_request() | NetworkInterface::process_request() (không đổi) |

### Design Pattern:

**CŨ:** Monolithic - NetworkInterface làm tất cả

**MỚI:** Delegation + Callback Pattern
- StreamServer: Chỉ lo stream/socket handling
- NetworkInterface: Chỉ lo business logic (gọi Python)
- Communication: Qua callback function

### Files thay đổi:

**CŨ:**
- `NetworkInterface.h` - Chứa socket code
- `NetworkInterface.cpp` - Chứa socket + business logic

**MỚI:**
- `NetworkInterface.h` - Chỉ khai báo, có StreamServer pointer
- `NetworkInterface.cpp` - Chỉ business logic
- `StreamServer.h` - Socket/Stream handling interface
- `StreamServer.cpp` - Socket/Stream handling implementation

---

## ✅ Lợi ích của kiến trúc mới

### 1. **Separation of Concerns**
- Stream handling tách biệt khỏi business logic
- Dễ test và maintain

### 2. **Reusability**
- StreamServer có thể dùng cho các server khác
- Chỉ cần truyền handler function khác

### 3. **Flexibility**
- Dễ thay đổi stream handling (ví dụ: thêm encryption)
- Business logic không bị ảnh hưởng

### 4. **Code Organization**
- NetworkInterface tập trung vào logic
- StreamServer tập trung vào networking

### 5. **Memory Management**
- Sử dụng `std::unique_ptr` - tự động cleanup
- Không cần manual delete

---

## 🔄 Flow Diagram - So sánh trực quan

### CŨ:
```
main() 
  → NetworkInterface::start()
    → Socket/Bind/Listen
    → Loop: accept()
      → handle_client() [thread]
        → process_request()
          → popen() → Python
        ← response
      ← send() to client
```

### MỚI:
```
main()
  → NetworkInterface(port)
    → StreamServer(port, handler_callback)
  → NetworkInterface::start()
    → StreamServer::start()
      → Socket/Bind/Listen
      → Loop: accept()
        → handleClient() [thread]
          → handler_callback(line) 
            → NetworkInterface::process_request()
              → popen() → Python
            ← response
          ← send() to client
```

---

## 📝 Tóm tắt

**Thay đổi chính:**
1. ✅ Tách stream handling thành `StreamServer` class riêng
2. ✅ NetworkInterface delegate stream handling cho StreamServer
3. ✅ Sử dụng callback pattern để giao tiếp
4. ✅ Business logic (`process_request`) không thay đổi

**Kết quả:**
- Code sạch hơn, có tổ chức hơn
- Dễ maintain và extend
- Separation of concerns rõ ràng

