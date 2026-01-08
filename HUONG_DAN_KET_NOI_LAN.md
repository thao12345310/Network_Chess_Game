# Hướng Dẫn Chạy Network Chess Game Trên Mạng LAN (Multi-Machine)

Tài liệu này hướng dẫn chi tiết cách thiết lập để chơi game giữa các máy tính khác nhau trong cùng mạng WiFi/LAN, khi Server chạy trên môi trường **WSL** (Windows).

## Tóm tắt quy trình
1.  **Trên máy chủ (Server Machine)**:
    *   Lấy IP của WSL.
    *   Lấy IP thực của Windows.
    *   Cấu hình Port Forwarding (chuyển tiếp cổng) từ Windows vào WSL.
    *   Mở Firewall.
    *   Chạy Server.
2.  **Trên máy khách (Client Machine)**:
    *   Chạy Client kết nối vào IP thực của máy chủ.

---

## PHẦN 1: THIẾT LẬP MÁY CHỦ (SERVER)

Thực hiện toàn bộ phần này trên máy tính sẽ chạy Server.

### Bước 1.1: Lấy thông tin IP WSL
Mở **Terminal Ubuntu/WSL** và chạy lệnh:
```bash
ip addr show eth0
```
Tìm dòng bắt đầu bằng `inet`.
*Ví dụ kết quả:* `inet 172.23.7.20/20...`
👉 **Ghi lại IP WSL này:** (Ví dụ: `172.23.7.20`)

### Bước 1.2: Lấy thông tin IP Windows (LAN IP)
Mở **PowerShell** hoặc **CMD** trên Windows và chạy:
```powershell
ipconfig
```
Tìm dòng **IPv4 Address** của card mạng bạn đang dùng (Wi-Fi hoặc Ethernet).
*Ví dụ kết quả:* `IPv4 Address . . . . . . . . . . . : 192.168.1.10`
👉 **Ghi lại IP Windows này:** (Ví dụ: `192.168.1.10`)

### Bước 1.3: Cấu hình Port Forwarding và Firewall (CHỈ LÀM 1 LẦN)
Mở **PowerShell với quyền Administrator** (Click phải vào Start -> Terminal (Admin) / PowerShell (Admin)).

Chạy lần lượt 2 lệnh sau (thay `172.23.7.20` bằng IP WSL bạn lấy ở Bước 1.1):

**Lệnh 1: Chuyển tiếp cổng (Port Forwarding)**
```powershell
# Thay ConnectAddress=172.23.7.20 bằng IP WSL của bạn
netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5001 connectaddress=172.23.7.20
```

**Lệnh 2: Mở Firewall cho cổng 5001**
```powershell
New-NetFirewallRule -DisplayName "Chess Server" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow
```

### Bước 1.4: Chạy Server
Quay lại **Terminal WSL**, vào thư mục project và chạy server:
```bash
cd server/src
./server
```
*Bạn phải thấy thông báo:* `Stream server listening on 0.0.0.0:5001`

---

## PHẦN 2: CHẠY MÁY KHÁCH (CLIENT)

### Trường hợp A: Chạy Client trên MÁY KHÁC (Bạn bè)
Trên máy tính của người chơi khác (phải cùng mạng WiFi/LAN):

1.  Mở Terminal/CMD tại thư mục project.
2.  Chạy lệnh kết nối vào **IP Windows** (lấy ở Bước 1.2):
    ```bash
    # Thay 192.168.1.10 bằng IP Windows của máy chủ
    cd ui
    python3 app_main.py --host 192.168.1.10
    ```

### Trường hợp B: Chạy Client trên MÁY CỦA BẠN (Máy chủ)
Nếu bạn vừa chạy server, vừa muốn chơi trên cùng máy đó:

1.  Mở thêm một Terminal WSL khác.
2.  Chạy lệnh:
    ```bash
    cd ui
    python3 app_main.py
    # Mặc định sẽ tự kết nối vào 127.0.0.1 (localhost)
    ```

---

## XỬ LÝ SỰ CỐ (TROUBLESHOOTING)

1.  **Lỗi "Connection refused" hoặc Connect mãi không được:**
    *   Kiểm tra lại IP Windows xem có đổi không (đôi khi reset modem sẽ bị đổi IP).
    *   Kiểm tra lại IP WSL. Mỗi lần tắt bật máy, IP WSL **thường xuyên thay đổi**.
    *   Nếu IP WSL thay đổi (ví dụ từ `.20` sang `.25`), bạn phải chạy lại lệnh `netsh` ở Bước 1.3 với IP mới.

2.  **Cách xóa Port Forwarding cũ (nếu cần):**
    ```powershell
    netsh interface portproxy delete v4tov4 listenport=5001 listenaddress=0.0.0.0
    ```

3.  **Kiểm tra xem Port Forwarding đã được cài chưa:**
    ```powershell
    netsh interface portproxy show all
    ```
