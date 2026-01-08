# Tính năng Game History & Replay

## Mô tả
Tính năng này cho phép người chơi xem lại lịch sử các ván đã chơi và replay lại các nước đi.

## Các thành phần đã thêm

### 1. Database Layer (`server/src/game_logic/db_handler.py`)
- **`get_player_game_history(player_id)`**: Lấy danh sách tất cả các ván đã chơi của người chơi
  - Trả về: game_id, mode, thời gian, kết quả, màu quân, đối thủ
  - Chỉ lấy các ván có status = 'FINISHED'
  - Sắp xếp theo thời gian mới nhất

### 2. Server Logic (`server/src/game_logic/logic_wrapper.py`)
- **Action `get_game_history`**: Lấy lịch sử game của người chơi
  - Input: `{"action": "get_game_history", "player_id": <id>}`
  - Output: `{"status": "success", "games": [...]}`

- **Action `get_game_replay`**: Lấy chi tiết game để replay
  - Input: `{"action": "get_game_replay", "game_id": <id>}`
  - Output: `{"status": "success", "game": {...}}`

### 3. UI Components

#### `screen_game_history.py`
Màn hình hiển thị danh sách các ván đã chơi:
- Hiển thị: Ngày, Mode, Đối thủ, Màu quân, Kết quả (WIN/LOSS/DRAW)
- Double-click hoặc nút "View Replay" để xem replay
- Nút "Refresh" để tải lại danh sách
- Nút "Back to Lobby" để quay lại

#### `screen_game_replay.py`
Màn hình replay với đầy đủ tính năng:
- **Bàn cờ**: Hiển thị trạng thái bàn cờ theo từng nước đi
- **Thông tin game**: Mode, người chơi, ELO, thời gian
- **Danh sách nước đi**: Click vào nước đi để nhảy đến vị trí đó
- **Điều khiển playback**:
  - ⏮ First: Về vị trí ban đầu
  - ◀ Previous: Lùi 1 nước
  - ▶/⏸ Play/Pause: Tự động chạy các nước đi
  - ▶ Next: Tiến 1 nước
  - ⏭ Last: Đến nước cuối cùng
- **Auto-play**: Tự động chạy các nước đi với tốc độ 1 giây/nước

### 4. Integration

#### `app_main.py`
- Thêm `player_id` để lưu ID người chơi sau khi login
- Khởi tạo `GameHistoryScreen` và `GameReplayScreen`
- Thêm methods `show_game_history()` và `show_game_replay()`

#### `screen_login.py`
- Cập nhật `on_login_response()` để trích xuất và truyền `player_id`

#### `screen_lobby.py`
- Thêm nút "📜 Game History" trong Quick Actions
- Callback `on_view_game_history` để mở màn hình lịch sử

## Cách sử dụng

### Từ Lobby Screen:
1. Click vào nút **"📜 Game History"** trong panel Quick Actions
2. Màn hình Game History sẽ hiển thị danh sách các ván đã chơi

### Trong Game History Screen:
1. Xem danh sách các ván đã chơi với thông tin:
   - Ngày giờ kết thúc
   - Mode (BLITZ/RAPID/CLASSICAL)
   - Tên đối thủ
   - Màu quân của bạn (WHITE/BLACK)
   - Kết quả (WIN/LOSS/DRAW)

2. Double-click vào một ván hoặc chọn và click **"🎬 View Replay"**

### Trong Game Replay Screen:
1. **Xem thông tin game**: Panel bên phải hiển thị mode, người chơi, ELO, thời gian
2. **Xem danh sách nước đi**: Panel bên phải hiển thị tất cả các nước đi
3. **Điều khiển playback**:
   - Click các nút điều khiển để di chuyển qua các nước đi
   - Click vào danh sách nước đi để nhảy đến nước đó
   - Click Play (▶) để tự động chạy các nước đi
   - Click Pause (⏸) để dừng auto-play

4. Click **"← Back"** để quay lại Game History

## Dependencies

### Python packages cần thiết:
```bash
pip install python-chess
```

Thư viện `python-chess` được sử dụng để:
- Parse và validate các nước đi UCI
- Quản lý trạng thái bàn cờ
- Hiển thị bàn cờ với các quân cờ

## Lưu ý kỹ thuật

1. **Database**: Tính năng này sử dụng bảng `Game` và `Move` hiện có, không cần migration
2. **Performance**: Chỉ load các ván có status = 'FINISHED' để tránh load quá nhiều dữ liệu
3. **Communication**: Gọi trực tiếp `logic_wrapper.py` qua subprocess thay vì qua C++ client (vì không cần realtime)
4. **Board rendering**: Sử dụng Tkinter Canvas để vẽ bàn cờ, không cần thư viện đồ họa phức tạp

## Cải tiến trong tương lai

1. **Filtering**: Thêm bộ lọc theo mode, kết quả, đối thủ
2. **Sorting**: Cho phép sắp xếp theo các tiêu chí khác nhau
3. **Export**: Xuất game ra file PGN
4. **Analysis**: Thêm tính năng phân tích nước đi
5. **Speed control**: Cho phép điều chỉnh tốc độ auto-play
6. **Annotations**: Thêm ghi chú vào các nước đi
