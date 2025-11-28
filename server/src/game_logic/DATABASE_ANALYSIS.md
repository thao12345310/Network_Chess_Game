# Phân tích Database Schema - So sánh với ERD và Code hiện tại

## 📊 So sánh Schema với ERD

### ✅ Schema hiện tại ĐỦ về cấu trúc:

| Bảng | ERD yêu cầu | Schema hiện tại | Trạng thái |
|------|-------------|-----------------|------------|
| **Player** | ✅ player_id (PK)<br>✅ username (NOT NULL, UNIQUE)<br>✅ password (NOT NULL)<br>✅ elo (DEFAULT 1200) | ✅ player_id (PK, AUTOINCREMENT)<br>✅ username (NOT NULL, UNIQUE)<br>✅ password (NOT NULL)<br>⚠️ elo (DEFAULT 1000) | ⚠️ **Sai DEFAULT** |
| **Game** | ✅ game_id (PK)<br>✅ white_id (FK, NOT NULL)<br>✅ black_id (FK, NOT NULL)<br>✅ winner_id (FK)<br>✅ mode (enum)<br>✅ start_time (string)<br>✅ end_time (string)<br>✅ status (enum) | ✅ game_id (PK, AUTOINCREMENT)<br>✅ white_id (FK, NOT NULL)<br>✅ black_id (FK, NOT NULL)<br>✅ winner_id (FK)<br>✅ mode (TEXT CHECK)<br>✅ start_time (TEXT)<br>✅ end_time (TEXT)<br>✅ status (TEXT CHECK, DEFAULT 'ONGOING') | ✅ **Đủ** |
| **Move** | ✅ move_id (PK)<br>✅ game_id (FK, NOT NULL)<br>✅ player_id (FK, NOT NULL)<br>✅ move_notation (string) | ✅ move_id (PK, AUTOINCREMENT)<br>✅ game_id (FK, NOT NULL)<br>✅ player_id (FK, NOT NULL)<br>✅ move_notation (TEXT NOT NULL) | ✅ **Đủ** |

---

## 🐛 Vấn đề phát hiện

### 1. ⚠️ DEFAULT ELO không khớp với ERD

**ERD yêu cầu:** `elo DEFAULT 1200`  
**Schema hiện tại:** `elo INTEGER DEFAULT 1000`

**Cần sửa:**
```sql
-- Trong init_db.py, dòng 14
elo INTEGER DEFAULT 1000  -- ❌ SAI
elo INTEGER DEFAULT 1200  -- ✅ ĐÚNG
```

---

## 🔍 Phân tích Functions hiện có

### ✅ Functions đã có trong `db_handler.py`:

| Function | Mô tả | Sử dụng đúng |
|----------|-------|--------------|
| `insert_move()` | Lưu nước đi | ✅ |
| `get_moves()` | Lấy danh sách nước đi | ✅ |
| `update_player_elo()` | Cập nhật ELO | ✅ |
| `update_game_result()` | Cập nhật kết quả game | ✅ |

### ⚠️ Actions đã có trong `logic_wrapper.py`:

| Action | Function gọi | Status |
|--------|--------------|--------|
| `validate_move` | `game_logic.validate_move()` | ✅ |
| `game_result` | `game_logic.determine_result()` | ✅ |
| `calculate_elo` | `elo_system.calculate_elo()` | ✅ |
| `update_elo` | `db_handler.update_player_elo()` | ✅ |
| `log_move` | `db_handler.insert_move()` | ✅ |
| `get_replay` | `db_handler.get_moves()` | ✅ |
| `update_game_result` | `db_handler.update_game_result()` | ✅ |

---

## ❌ Các Functions/Actions THIẾU

### 1. **Player Management** - Quản lý người chơi

#### ❌ THIẾU: Đăng ký player mới
**Client code có:** `registerAccount()` trong `GameClient.cpp`  
**Server thiếu:** Action `register_player` trong `logic_wrapper.py`

**Cần thêm:**
```python
# Trong db_handler.py
def create_player(username, password, elo=1200):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Player (username, password, elo) VALUES (?, ?, ?)",
            (username, password, elo)
        )
        player_id = cur.lastrowid
        conn.commit()
        return player_id
    except sqlite3.IntegrityError:
        return None  # Username đã tồn tại
    finally:
        conn.close()

def get_player_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT player_id, username, password, elo FROM Player WHERE username = ?",
        (username,)
    )
    player = cur.fetchone()
    conn.close()
    return player  # (player_id, username, password, elo) hoặc None

def authenticate_player(username, password):
    player = get_player_by_username(username)
    if player and player[2] == password:  # password ở index 2
        return player[0]  # return player_id
    return None

def get_player_info(player_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT player_id, username, elo FROM Player WHERE player_id = ?",
        (player_id,)
    )
    player = cur.fetchone()
    conn.close()
    return player
```

**Actions cần thêm trong `logic_wrapper.py`:**
```python
elif action == 'register_player':
    username = req.get('username')
    password = req.get('password')
    player_id = create_player(username, password)
    if player_id:
        response = {"status": "success", "player_id": player_id}
    else:
        response = {"status": "error", "message": "Username already exists"}

elif action == 'login':
    username = req.get('username')
    password = req.get('password')
    player_id = authenticate_player(username, password)
    if player_id:
        response = {"status": "success", "player_id": player_id}
    else:
        response = {"status": "error", "message": "Invalid credentials"}

elif action == 'get_player_info':
    player_id = req.get('player_id')
    player = get_player_info(player_id)
    if player:
        response = {"status": "success", "player_id": player[0], "username": player[1], "elo": player[2]}
    else:
        response = {"status": "error", "message": "Player not found"}
```

---

### 2. **Game Management** - Quản lý game

#### ❌ THIẾU: Tạo game mới
**Client code có:** `sendChallenge()` để tạo game  
**Server thiếu:** Action `create_game` trong `logic_wrapper.py`

**Cần thêm:**
```python
# Trong db_handler.py
def create_game(white_id, black_id, mode='CLASSICAL'):
    conn = get_connection()
    cur = conn.cursor()
    import datetime
    cur.execute(
        """
        INSERT INTO Game (white_id, black_id, mode, start_time, status)
        VALUES (?, ?, ?, ?, 'ONGOING')
        """,
        (white_id, black_id, mode, datetime.datetime.utcnow().isoformat())
    )
    game_id = cur.lastrowid
    conn.commit()
    conn.close()
    return game_id

def get_game_info(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT game_id, white_id, black_id, mode, start_time, end_time, 
               winner_id, status 
        FROM Game 
        WHERE game_id = ?
        """,
        (game_id,)
    )
    game = cur.fetchone()
    conn.close()
    return game

def get_player_games(player_id, status=None):
    conn = get_connection()
    cur = conn.cursor()
    if status:
        cur.execute(
            """
            SELECT game_id, white_id, black_id, mode, start_time, end_time, 
                   winner_id, status 
            FROM Game 
            WHERE (white_id = ? OR black_id = ?) AND status = ?
            ORDER BY start_time DESC
            """,
            (player_id, player_id, status)
        )
    else:
        cur.execute(
            """
            SELECT game_id, white_id, black_id, mode, start_time, end_time, 
                   winner_id, status 
            FROM Game 
            WHERE white_id = ? OR black_id = ?
            ORDER BY start_time DESC
            """,
            (player_id, player_id)
        )
    games = cur.fetchall()
    conn.close()
    return games
```

**Actions cần thêm trong `logic_wrapper.py`:**
```python
elif action == 'create_game':
    white_id = req.get('white_id')
    black_id = req.get('black_id')
    mode = req.get('mode', 'CLASSICAL')
    game_id = create_game(white_id, black_id, mode)
    response = {"status": "success", "game_id": game_id}

elif action == 'get_game_info':
    game_id = req.get('game_id')
    game = get_game_info(game_id)
    if game:
        response = {
            "status": "success",
            "game_id": game[0],
            "white_id": game[1],
            "black_id": game[2],
            "mode": game[3],
            "start_time": game[4],
            "end_time": game[5],
            "winner_id": game[6],
            "status": game[7]
        }
    else:
        response = {"status": "error", "message": "Game not found"}

elif action == 'get_player_games':
    player_id = req.get('player_id')
    status = req.get('status')  # Optional filter
    games = get_player_games(player_id, status)
    games_list = []
    for game in games:
        games_list.append({
            "game_id": game[0],
            "white_id": game[1],
            "black_id": game[2],
            "mode": game[3],
            "start_time": game[4],
            "end_time": game[5],
            "winner_id": game[6],
            "status": game[7]
        })
    response = {"status": "success", "games": games_list}
```

---

### 3. **Player List** - Danh sách người chơi

#### ❌ THIẾU: Lấy danh sách players
**Client code có:** `requestPlayerList()` trong `GameClient.cpp`  
**Server thiếu:** Action `get_player_list` trong `logic_wrapper.py`

**Cần thêm:**
```python
# Trong db_handler.py
def get_all_players():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT player_id, username, elo FROM Player ORDER BY elo DESC"
    )
    players = cur.fetchall()
    conn.close()
    return players
```

**Action cần thêm trong `logic_wrapper.py`:**
```python
elif action == 'get_player_list':
    players = get_all_players()
    players_list = []
    for player in players:
        players_list.append({
            "player_id": player[0],
            "username": player[1],
            "elo": player[2]
        })
    response = {"status": "success", "players": players_list}
```

---

## 📋 Tóm tắt những gì THIẾU

### Database Schema:
- ⚠️ **DEFAULT elo = 1000** (nên là 1200 theo ERD)

### Database Functions (`db_handler.py`):
- ❌ `create_player()` - Tạo player mới
- ❌ `get_player_by_username()` - Lấy player theo username
- ❌ `authenticate_player()` - Xác thực player
- ❌ `get_player_info()` - Lấy thông tin player
- ❌ `get_all_players()` - Lấy danh sách tất cả players
- ❌ `create_game()` - Tạo game mới
- ❌ `get_game_info()` - Lấy thông tin game
- ❌ `get_player_games()` - Lấy danh sách games của player

### Actions (`logic_wrapper.py`):
- ❌ `register_player` - Đăng ký
- ❌ `login` - Đăng nhập
- ❌ `get_player_info` - Lấy thông tin player
- ❌ `get_player_list` - Lấy danh sách players
- ❌ `create_game` - Tạo game
- ❌ `get_game_info` - Lấy thông tin game
- ❌ `get_player_games` - Lấy lịch sử games (match history)

---

## 🎯 Ưu tiên sửa

### Priority 1 (Quan trọng - Client code đã có):
1. ✅ Sửa DEFAULT elo từ 1000 → 1200
2. ❌ Thêm `register_player` action
3. ❌ Thêm `login` action
4. ❌ Thêm `get_player_list` action
5. ❌ Thêm `create_game` action
6. ❌ Thêm `get_player_games` action (cho match history)

### Priority 2 (Hữu ích):
7. ❌ Thêm `get_player_info` action
8. ❌ Thêm `get_game_info` action

---

## ✅ Kết luận

**Database schema:** ✅ **Đủ** (chỉ cần sửa DEFAULT elo)

**Database functions:** ❌ **Thiếu nhiều** - Cần thêm 8 functions

**API actions:** ❌ **Thiếu nhiều** - Cần thêm 7 actions để phù hợp với client code

**Vấn đề:** Client code (GameClient.cpp) có các functions nhưng server không có actions tương ứng → **Không thể hoạt động được!**

