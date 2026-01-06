# Hướng dẫn Build và Chạy

## Vấn đề hiện tại
Lỗi `'NoneType' object has no attribute 'get'` khi login xảy ra vì:
1. C++ client chưa được rebuild với message format mới
2. Client vẫn gửi message theo format cũ, server không hiểu → không trả về response

## Giải pháp: Rebuild C++ Client

### Bước 1: Clean build cũ
```bash
cd client
make clean
```

### Bước 2: Build lại client
```bash
make
```

### Bước 3: Copy thư viện sang UI folder
```bash
make install
```

Hoặc chạy tất cả cùng lúc:
```bash
cd client && make clean && make && make install
```

### Bước 4: Kiểm tra file .so đã được copy
```bash
ls -la ui/libchessclient.so
```

Bạn sẽ thấy file với timestamp mới (vừa được build).

## Chạy ứng dụng

### Chạy Server (terminal 1)
```bash
cd server/src/game_logic
python3 main.cpp  # hoặc ./server nếu đã build C++
```

### Chạy UI Client (terminal 2)
```bash
cd ui
python3 app_main.py
```

## Debug

Nếu vẫn gặp lỗi, kiểm tra:
1. Server có chạy không: `ps aux | grep python`
2. File .so đã được update chưa: `stat ui/libchessclient.so`
3. Xem log debug khi chạy UI để biết message được gửi như thế nào

## Message Format Mới

Client giờ gửi:
```json
{
  "messageType": "AUTH_LOGIN_REQ",
  "payload": {
    "username": "...",
    "password": "..."
  }
}
```

Thay vì format cũ:
```json
{
  "type": "LOGIN",
  "username": "...",
  "password": "..."
}
```
