# Custom Board Setup - Practice Mode

## Tính năng mới: Tự setup bàn cờ và chơi với chính mình

Tính năng **Custom Board Setup** cho phép bạn:
- ✅ Tự setup vị trí các quân cờ trên bàn cờ
- ✅ Chơi với chính mình (Practice Mode)
- ✅ Luyện tập các tình huống đặc biệt (endgame, tactics)
- ✅ Phân tích các vị trí cụ thể
- ✅ Không giới hạn thời gian

## Cách sử dụng

### 1. Vào màn hình Board Setup
Từ **Lobby**, click vào nút **"♟️ Custom Board Setup"**

### 2. Setup bàn cờ

#### Chọn quân cờ:
- **White Pieces**: ♙ ♘ ♗ ♖ ♕ ♔
- **Black Pieces**: ♟ ♞ ♝ ♜ ♛ ♚

Click vào quân cờ muốn đặt, sau đó click vào ô trên bàn cờ để đặt quân.

#### Các nút điều khiển:
- **🗑️ Eraser**: Xóa quân cờ trên bàn (click vào ô để xóa)
- **Clear Board**: Xóa toàn bộ bàn cờ
- **Standard Position**: Reset về vị trí chuẩn ban đầu

### 3. Cấu hình trò chơi

#### Turn to move:
Chọn bên nào đi trước:
- **White**: Trắng đi trước
- **Black**: Đen đi trước

#### FEN Position:
Hiển thị FEN string của vị trí hiện tại. Bạn có thể:
- **Copy FEN**: Sao chép FEN để lưu hoặc chia sẻ

### 4. Validation

Hệ thống tự động kiểm tra vị trí hợp lệ:
- ✓ **Phải có đúng 1 vua mỗi bên**
- ✓ **Không có quân tốt ở hàng 1 hoặc hàng 8**
- ⚠️ Nếu có lỗi, nút "Start Practice" sẽ bị vô hiệu hóa

Khi vị trí hợp lệ, hiển thị: ✓ Valid position

### 5. Bắt đầu Practice Mode

Click **"▶ Start Practice"** để bắt đầu chơi.

## Đặc điểm Practice Mode

### Trong Practice Mode:
- 🎮 **Chơi với chính mình**: Bạn có thể di chuyển cả quân trắng và quân đen
- ♾️ **Không giới hạn thời gian**: Suy nghĩ thoải mái
- 🔄 **Có thể thử các nước đi khác nhau**: Phân tích các biến thể
- 📊 **ELO không bị ảnh hưởng**: Chỉ để luyện tập

### Thoát Practice Mode:
- Click **"Back"** hoặc thoát trò chơi để quay lại Lobby

## Ví dụ sử dụng

### 1. Luyện tập Endgame
Setup:
- Vua trắng + Hậu trắng
- Vua đen
- Luyện chiếu hết với Vua + Hậu

### 2. Puzzle Tactics
Setup:
- Một vị trí cụ thể từ tactics puzzle
- Thử tìm nước đi tốt nhất

### 3. Phân tích vị trí
Setup:
- Vị trí từ một ván cờ thực
- Phân tích các biến thể khác nhau

## Yêu cầu kỹ thuật

### Dependencies:
```bash
pip install chess  # python-chess library
```

### Files liên quan:
- `ui/screen_board_setup.py` - Màn hình setup board
- `ui/chess_board.py` - Logic bàn cờ (thêm load_fen method)
- `ui/screen_game.py` - Hỗ trợ custom FEN
- `ui/app_main.py` - Tích hợp vào app
- `server/src/game_logic/db_handler.py` - Hỗ trợ custom FEN khi tạo game

## Tips

### 1. Sử dụng FEN
Bạn có thể copy FEN từ:
- Lichess.org
- Chess.com
- Các engine phân tích cờ

Paste vào một file text để lưu các vị trí thú vị.

### 2. Kiểm tra vị trí hợp lệ
Đảm bảo:
- Mỗi bên có đúng 1 vua
- Không có tốt ở hàng 1 hoặc 8
- Vị trí có thể đạt được trong ván cờ thực

### 3. Practice các tình huống
- **Checkmate patterns**: Học các mẫu chiếu hết cơ bản
- **Endgame theory**: Luyện các endgame quan trọng
- **Tactics**: Luyện fork, pin, skewer, discovered attack...

## Hạn chế hiện tại

- ⚠️ **Castling rights**: Mặc định set tất cả castling available
- ⚠️ **En passant**: Không support en passant square trong setup
- ⚠️ **Halfmove clock**: Reset về 0
- ⚠️ **Chỉ chơi local**: Không thể chơi practice mode với người khác

## Future improvements

Có thể cải thiện:
1. ✨ Paste FEN từ clipboard
2. ✨ Load vị trí từ PGN
3. ✨ Thư viện các vị trí phổ biến (preset positions)
4. ✨ Integration với Stockfish để phân tích
5. ✨ Lưu các vị trí custom

## Liên hệ

Nếu có câu hỏi hoặc đóng góp ý tưởng, vui lòng tạo issue trên GitHub.

---
**Chúc bạn luyện tập vui vẻ! ♟️**
