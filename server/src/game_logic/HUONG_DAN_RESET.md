# HƯỚNG DẪN RESET DATABASE VÀ CHẠY LẠI TỪ ĐẦU

## Cách 1: Dùng Script Tự Động (Khuyến nghị)

### Bước 1: Mở Terminal/PowerShell
Mở terminal và di chuyển đến thư mục game_logic:
```bash
cd D:\Network_Chess_Game\server\src\game_logic
```

### Bước 2: Chạy Script Reset
```bash
python reset_db.py
```

Script này sẽ tự động:
- ✅ Xóa database cũ (nếu có)
- ✅ Khởi tạo lại database mới với schema đầy đủ
- ✅ Tạo 2 players test (alice và bob)
- ✅ Tạo 1 game mới
- ✅ Thực hiện nước đi đầu tiên (e2e4)
- ✅ Hiển thị kết quả

---

## Cách 2: Làm Thủ Công Từng Bước

### Bước 1: Xóa Database Cũ
```bash
cd D:\Network_Chess_Game\server\src\game_logic
del chess_game.db
```

Hoặc nếu có nhiều file database:
```bash
del *.db
```

### Bước 2: Khởi Tạo Database Mới
```bash
python init_db.py
```

Bạn sẽ thấy thông báo: `✅ Database initialized successfully!`

### Bước 3: Chạy Demo Tạo Game và Make Move
```bash
python run_demo.py
```

---

## Kiểm Tra Kết Quả

Sau khi chạy xong, bạn có thể kiểm tra database bằng SQLite:

```bash
sqlite3 chess_game.db
```

Trong SQLite shell:
```sql
-- Xem danh sách players
SELECT * FROM Player;

-- Xem danh sách games
SELECT * FROM Game;

-- Xem danh sách moves
SELECT * FROM Move;
```

---

## Lưu Ý

1. **Đảm bảo đã cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Nếu gặp lỗi "Module not found":**
   - Đảm bảo bạn đang ở đúng thư mục: `D:\Network_Chess_Game\server\src\game_logic`
   - Kiểm tra Python path: `python --version`

3. **Database được tạo ở đâu:**
   - Database file: `D:\Network_Chess_Game\server\src\game_logic\chess_game.db`
   - File này sẽ được tạo tự động khi chạy `init_db.py` hoặc `reset_db.py`

---

## Troubleshooting

### Lỗi: "database is locked"
- Đóng tất cả các kết nối đến database
- Đảm bảo không có server nào đang chạy và sử dụng database

### Lỗi: "No module named 'chess'"
```bash
pip install python-chess
```

### Lỗi: "No module named 'database'"
- Đảm bảo bạn đang ở đúng thư mục: `D:\Network_Chess_Game\server\src\game_logic`
- Tất cả các file Python phải ở cùng một thư mục

