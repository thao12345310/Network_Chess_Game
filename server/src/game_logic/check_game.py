"""
Script để kiểm tra trạng thái game trong database
"""
import sqlite3
from database import get_connection, DB_NAME
import os

def check_database():
    """Kiểm tra database và hiển thị thông tin"""
    if not os.path.exists(DB_NAME):
        print(f"❌ Database không tồn tại: {DB_NAME}")
        print("💡 Chạy: python reset_db.py để tạo database mới")
        return
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Kiểm tra players
    cur.execute("SELECT COUNT(*) FROM Player")
    player_count = cur.fetchone()[0]
    print(f"📊 Số lượng players: {player_count}")
    
    if player_count > 0:
        cur.execute("SELECT player_id, username, elo FROM Player")
        players = cur.fetchall()
        print("\n👥 Danh sách players:")
        for pid, username, elo in players:
            print(f"   - ID: {pid}, Username: {username}, ELO: {elo}")
    
    # Kiểm tra games
    cur.execute("SELECT COUNT(*) FROM Game")
    game_count = cur.fetchone()[0]
    print(f"\n📊 Số lượng games: {game_count}")
    
    if game_count > 0:
        cur.execute("""
            SELECT game_id, white_id, black_id, status, current_fen 
            FROM Game 
            ORDER BY game_id
        """)
        games = cur.fetchall()
        print("\n🎮 Danh sách games:")
        for gid, wid, bid, status, fen in games:
            print(f"\n   Game ID: {gid}")
            print(f"   - White ID: {wid}, Black ID: {bid}")
            print(f"   - Status: {status}")
            if fen:
                # Parse FEN để xem turn
                parts = fen.split()
                turn = parts[1] if len(parts) > 1 else "N/A"
                print(f"   - Current FEN: {fen[:50]}...")
                print(f"   - Turn: {'White' if turn == 'w' else 'Black' if turn == 'b' else 'Unknown'}")
            else:
                print(f"   - Current FEN: NULL (⚠️ VẤN ĐỀ!)")
    
    # Kiểm tra moves
    cur.execute("SELECT COUNT(*) FROM Move")
    move_count = cur.fetchone()[0]
    print(f"\n📊 Số lượng moves: {move_count}")
    
    if move_count > 0:
        cur.execute("""
            SELECT move_id, game_id, player_id, move_notation 
            FROM Move 
            ORDER BY move_id
            LIMIT 10
        """)
        moves = cur.fetchall()
        print("\n♟️  Một số moves gần đây:")
        for mid, gid, pid, move in moves:
            print(f"   - Move {mid}: Game {gid}, Player {pid}, Move: {move}")
    
    conn.close()
    
    # Đưa ra khuyến nghị
    print("\n" + "="*60)
    if game_count == 0:
        print("⚠️  KHÔNG CÓ GAME NÀO TRONG DATABASE!")
        print("💡 Chạy: python reset_db.py để tạo game mới")
    elif player_count == 0:
        print("⚠️  KHÔNG CÓ PLAYERS NÀO TRONG DATABASE!")
        print("💡 Chạy: python reset_db.py để tạo players và game")
    else:
        print("✅ Database có dữ liệu. Bạn có thể chơi game!")

if __name__ == "__main__":
    check_database()

