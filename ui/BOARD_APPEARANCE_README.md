# Board Appearance Settings - Hướng Dẫn Sử Dụng

## Tổng Quan
Tính năng tùy chỉnh giao diện bàn cờ cho phép người chơi cá nhân hóa trải nghiệm chơi game.

## Các Files Mới
- `board_themes.py` - Định nghĩa các theme và piece styles
- `appearance_settings.py` - Quản lý lưu/load settings
- `screen_appearance.py` - UI màn hình settings
- `board_settings.json` - File lưu preferences (tự động tạo)

## Tính Năng

### 1. Board Themes (Màu Bàn Cờ)
7 themes có sẵn:
- **Classic** - Màu truyền thống (#F0D9B5 / #B58863)
- **Wood** - Gỗ tự nhiên (#D4A574 / #8B5A3C)
- **Dark** - Tối (#4A4A4A / #2C2C2C)
- **Modern** - Hiện đại (#EEEEEE / #6C7A89)
- **Ocean Blue** - Xanh biển (#B3E5FC / #4FC3F7)
- **Royal Purple** - Tím hoàng gia (#E1BEE7 / #9C27B0)
- **Forest Green** - Xanh rừng (#C5E1A5 / #558B2F)

### 2. Piece Styles (Kiểu Quân Cờ)
4 styles có sẵn:
- **Classic** - Arial 48px, đen
- **Bold** - Arial Black 52px, đậm
- **Modern** - Segoe UI 50px
- **Elegant** - Georgia 48px, thanh lịch

### 3. Display Options
- ✅ **Show Coordinates** - Hiển thị tọa độ (a-h, 1-8)
- ✅ **Show Legal Move Indicators** - Hiển thị chấm tròn cho nước đi hợp lệ

## Cách Sử Dụng

### Từ Lobby:
1. Click button **"⚙️ Board Settings"** ở lobby
2. Chọn theme/style mong muốn
3. Preview realtime trên board nhỏ 4x4
4. Click **"⬅️ Back to Lobby"** khi xong
5. Settings tự động lưu và áp dụng cho tất cả game

### Trong Game:
- Theme đã chọn sẽ tự động áp dụng
- Thay đổi settings trong game sẽ không ảnh hưởng đến game đang chơi
- Game mới sẽ dùng settings mới nhất

## Lưu Settings
- Settings tự động lưu vào file `board_settings.json`
- File này ở cùng folder với `app_main.py`
- Format: JSON với các keys:
  ```json
  {
    "board_theme": "classic",
    "piece_style": "classic",
    "show_coordinates": true,
    "show_legal_moves": true,
    "square_size": 80
  }
  ```

## Reset Defaults
Click button **"🔄 Reset to Defaults"** để về settings mặc định.

## Mở Rộng Themes

### Thêm Theme Mới:
Chỉnh file `board_themes.py`, thêm vào `THEMES` dictionary:
```python
'your_theme': {
    'name': 'Your Theme Name',
    'light_square': '#RRGGBB',
    'dark_square': '#RRGGBB',
    'selected': '#RRGGBB',
    'valid_move_light': '#RRGGBB',
    'valid_move_dark': '#RRGGBB',
    'capture_ring': '#RRGGBB',
    'move_indicator': '#RRGGBB'
}
```

### Thêm Piece Style Mới:
```python
'your_style': {
    'name': 'Your Style Name',
    'pieces': {
        'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
        'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
    },
    'font': ('FontName', size),
    'color': '#RRGGBB'
}
```

## Technical Details

### Architecture:
```
AppearanceSettings (singleton-like)
    ↓
ChessBoard (uses theme/style)
    ↓
GameScreen (displays board)
    ↓
AppearanceScreen (settings UI)
```

### Data Flow:
1. User thay đổi settings → `AppearanceScreen`
2. Update `appearance_settings` object
3. Save to `board_settings.json`
4. `ChessBoard` load từ `appearance_settings`
5. Re-draw với theme/style mới

## Troubleshooting

### Settings không lưu?
- Kiểm tra quyền write file trong folder
- Xóa `board_settings.json` và restart app

### Theme không áp dụng?
- Restart app hoặc back to lobby rồi vào game mới
- Check console logs

### Preview không hiển thị đúng?
- Font có thể không support trên OS
- Thử style khác hoặc dùng system fonts

## Future Enhancements
- [ ] Custom colors picker
- [ ] Import/export themes
- [ ] Image-based pieces
- [ ] Animated pieces
- [ ] Sound effects per theme
- [ ] Board size adjustment (slider)
