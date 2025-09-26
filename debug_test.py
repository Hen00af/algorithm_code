from main import MyAI

def test_basic():
    """基本的な動作テスト"""
    # 空のボードでテスト
    cube = [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    ai = MyAI()
    
    print("Testing empty board...")
    result = ai.get_move(cube, 1, [0, 0, 0])
    print(f"Result for empty board: {result}")
    
    # 一手打った後のテスト
    cube[0][0][0] = 1  # プレイヤー1が(0,0,0)に配置
    print("\nTesting after one move...")
    result = ai.get_move(cube, 2, [0, 0, 0])
    print(f"Result after player 1 at (0,0,0): {result}")
    
    # 勝利手のテスト
    cube2 = [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    cube2[0][0][0] = 2  # プレイヤー2
    cube2[0][0][1] = 2  # プレイヤー2
    cube2[0][0][2] = 2  # プレイヤー2
    # cube2[0][0][3] = 0  # 空き - プレイヤー2が勝てる
    
    print("\nTesting winning move...")
    result = ai.get_move(cube2, 2, [0, 0, 2])
    print(f"Result for winning move opportunity: {result}")

if __name__ == "__main__":
    test_basic()
