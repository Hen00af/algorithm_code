from main import MyAI
import copy

def test_game_sequence():
    """実際のゲーム進行をシミュレート"""
    # 空のボード
    board = [[[0 for _ in range(4)] for _ in range(4)] for _ in range(4)]
    ai = MyAI()
    
    # ゲーム進行をシミュレート
    moves = [
        (1, (0, 0)),  # 1手目 黒 (0, 0)
        (2, (0, 3)),  # 2手目 白 (0, 3)
        (1, (0, 1)),  # 3手目 黒 (0, 1)
        (2, (3, 0)),  # 4手目 白 (3, 0)
        (1, (1, 1)),  # 5手目 黒 (1, 1)
        (2, (3, 3)),  # 6手目 白 (3, 3)
        (1, (1, 2)),  # 7手目 黒 (1, 2)
        (2, (1, 2)),  # 8手目 白 (1, 2) <- これは無効（既に配置済み）のはず
        (1, (0, 1)),  # 9手目 黒 (0, 1) <- これも無効（既に配置済み）のはず
        (2, (1, 2)),  # 10手目 白 (1, 2) <- これも無効
        (1, (0, 1)),  # 11手目 黒 (0, 1) <- これも無効
        (2, (0, 1)),  # 12手目 白 (0, 1) <- これも無効
    ]
    
    print("=== ゲームシミュレーション ===")
    
    # 手動でボードを構築（上記の手順に基づいて）
    board[0][0][0] = 1  # 1手目 黒
    board[0][3][0] = 2  # 2手目 白
    board[0][1][0] = 1  # 3手目 黒
    board[0][0][3] = 2  # 4手目 白
    board[0][1][1] = 1  # 5手目 黒
    board[0][3][3] = 2  # 6手目 白
    board[0][2][1] = 1  # 7手目 黒
    board[1][2][1] = 2  # 8手目 白（上に積む）
    # 9手目以降は無効手が続いているので、適切な手を打つ必要がある
    
    print("現在のボード状態:")
    for z in range(4):
        print(f"レベル {z}:")
        for y in range(4):
            row = []
            for x in range(4):
                row.append(board[z][y][x])
            print(f"  {row}")
        print()
    
    # 13手目（黒番）のAIの手を計算
    print("13手目（黒番）でのAIの判断:")
    try:
        result = ai.get_move(board, 1, (1, 2, 1))
        print(f"AI推奨手: {result}")
        
        # 合法手リストを確認
        legal_moves = ai.legal_move(board)
        print(f"利用可能な合法手: {len(legal_moves)} 手")
        for i, move in enumerate(legal_moves[:10]):  # 最初の10手のみ表示
            print(f"  {i+1}. {move} -> 出力座標: ({move[1]}, {move[2]})")
            
    except Exception as e:
        print(f"エラーが発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_game_sequence()
