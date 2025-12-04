"""
Script để reset và khởi tạo lại database từ đầu
"""
import os
import sys
from database import DB_NAME
from init_db import init_db
from run_demo import create_test_players_and_game, INITIAL_FEN


def reset_database():
    """Xóa database cũ và khởi tạo lại từ đầu"""
    # Xóa database cũ nếu tồn tại
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"✅ Đã xóa database cũ: {DB_NAME}")
    else:
        print(f"ℹ️  Không tìm thấy database cũ: {DB_NAME}")
    
    # Khởi tạo database mới
    print("\n🔄 Đang khởi tạo database mới...")
    init_db()
    print("✅ Database đã được khởi tạo thành công!\n")


def create_demo_game():
    """Tạo game demo với FEN ban đầu, sẵn sàng để chơi"""
    print("=" * 60)
    print("TẠO GAME DEMO - SẴN SÀNG ĐỂ CHƠI")
    print("=" * 60)
    
    # Tạo players và game
    print("\n📝 Đang tạo players và game...")
    white_id, black_id, game_id = create_test_players_and_game()
    print(f"✅ Đã tạo:")
    print(f"   - Player White (alice): ID {white_id}")
    print(f"   - Player Black (bob): ID {black_id}")
    print(f"   - Game ID: {game_id}")
    print(f"\n📊 Game đã được tạo với FEN ban đầu:")
    print(f"   {INITIAL_FEN}")
    print(f"\n🎮 Bạn có thể bắt đầu chơi ngay!")
    print(f"   - Game ID để sử dụng: {game_id}")
    print(f"   - Lượt đi đầu tiên: White (alice)")
    
    print("\n" + "=" * 60)
    print("HOÀN TẤT!")
    print("=" * 60)


def main():
    """Hàm main để reset và tạo game mới"""
    print("\n" + "=" * 60)
    print("RESET DATABASE VÀ TẠO GAME MỚI")
    print("=" * 60 + "\n")
    
    try:
        # Bước 1: Reset database
        reset_database()
        
        # Bước 2: Tạo game mới (không thực hiện nước đi)
        create_demo_game()
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

