from typing import List, Tuple
# from local_driver import Alg3D, Board  # ローカル検証用
from framework import Alg3D, Board      # 本番用

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]],  # 盤面情報 board[z][y][x]
        player: int,                   # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int]  # 直前に置かれた場所 (x, y, z)
    ) -> Tuple[int, int]:
        """
        中央寄りの列から順に探して、まだ空きがある列を選ぶ。
        戻り値は (x, y) で 0..3 の範囲。
        """

        BOARD_SIZE_X = 4
        BOARD_SIZE_Y = 4
        BOARD_SIZE_Z = len(board)

        # --- 1. 中央寄りの順序を作る (x,y のリスト) ---
        def center_priority_order(width, height):
            xs = list(range(width))
            ys = list(range(height))
            # 中央からの距離でソート
            xs_sorted = sorted(xs, key=lambda i: (abs(i - (width - 1) / 2), i))
            ys_sorted = sorted(ys, key=lambda j: (abs(j - (height - 1) / 2), j))
            order = []
            for y in ys_sorted:
                for x in xs_sorted:
                    order.append((x, y))
            return order

        # --- 2. その列に空きがあるか判定 ---
        def column_has_space(x, y):
            for z in range(BOARD_SIZE_Z):
                try:
                    if board[z][y][x] == 0:  # 空きマス発見
                        return True
                except IndexError:
                    # 万一盤サイズが想定外でも落ちない
                    pass
            return False

        # --- 3. 中央寄りから探索 ---
        for x, y in center_priority_order(BOARD_SIZE_X, BOARD_SIZE_Y):
            if column_has_space(x, y):
                return (x, y)

        # --- 4. フォールバック：左上から順に探す ---
        for y in range(BOARD_SIZE_Y):
            for x in range(BOARD_SIZE_X):
                if column_has_space(x, y):
                    return (x, y)

        # --- 5. 万一全て埋まっていた場合も (0,0) を返す ---
        return (0, 0)
