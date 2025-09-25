from typing import List, Tuple
from math import inf
# from local_driver import Alg3D, Board  # ローカル検証用
from framework import Alg3D, Board      # 本番用


class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]],
        player: int,
        last_move: Tuple[int, int, int]
    ) -> Tuple[int, int]:
        BOARD_SIZE_X, BOARD_SIZE_Y, BOARD_SIZE_Z = 4, 4, len(board)
        opponent = 2 if player == 1 else 1

        # --- 空きマス数を数えて深さを可変に ---
        empty_count = sum(
            board[z][y][x] == 0
            for z in range(BOARD_SIZE_Z)
            for y in range(BOARD_SIZE_Y)
            for x in range(BOARD_SIZE_X)
        )
        if empty_count > 10:
            MAX_DEPTH = 3   # 序盤
        elif empty_count > 5:
            MAX_DEPTH = 4   # 中盤
        else:
            MAX_DEPTH = 5   # 終盤じっくり

        # ---- 中央優先順序を生成 ----
        def center_priority_order():
            xs = list(range(BOARD_SIZE_X))
            ys = list(range(BOARD_SIZE_Y))
            xs_sorted = sorted(xs, key=lambda i: (abs(i - 1.5), i))
            ys_sorted = sorted(ys, key=lambda j: (abs(j - 1.5), j))
            order = []
            for y in ys_sorted:
                for x in xs_sorted:
                    order.append((x, y))
            return order

        order = center_priority_order()

        # ---- 盤面ユーティリティ ----
        def column_has_space(x, y):
            for z in range(BOARD_SIZE_Z):
                if board[z][y][x] == 0:
                    return True
            return False

        def get_lowest_empty_z(x, y):
            for z in range(BOARD_SIZE_Z):
                if board[z][y][x] == 0:
                    return z
            return None

        def make_move(state, x, y, p):
            z = get_lowest_empty_z(x, y)
            if z is not None:
                state[z][y][x] = p
                return True
            return False

        def undo_move(state, x, y):
            for z in reversed(range(BOARD_SIZE_Z)):
                if state[z][y][x] != 0:
                    state[z][y][x] = 0
                    return

        # ---- 評価関数 ----
        def evaluate(state, p):
            score = 0
            lines = []
            for z in range(BOARD_SIZE_Z):
                for y in range(BOARD_SIZE_Y):
                    for x in range(BOARD_SIZE_X):
                        if x <= BOARD_SIZE_X - 4:
                            lines.append([state[z][y][x+i] for i in range(4)])
                        if y <= BOARD_SIZE_Y - 4:
                            lines.append([state[z][y+i][x] for i in range(4)])
                        if z <= BOARD_SIZE_Z - 4:
                            lines.append([state[z+i][y][x] for i in range(4)])
                        if x <= BOARD_SIZE_X - 4 and y <= BOARD_SIZE_Y - 4 and z <= BOARD_SIZE_Z - 4:
                            lines.append([state[z+i][y+i][x+i] for i in range(4)])

            for line in lines:
                if line.count(p) == 4:
                    return 10000
                elif line.count(p) == 3 and line.count(0) == 1:
                    score += 50
                elif line.count(p) == 2 and line.count(0) == 2:
                    score += 10

            for z in range(BOARD_SIZE_Z):
                for y in range(BOARD_SIZE_Y):
                    for x in range(BOARD_SIZE_X):
                        if state[z][y][x] == p:
                            score += (2 - abs(x - 1.5)) + (2 - abs(y - 1.5))

            return score

        # ---- Minimax + αβ枝刈り ----
        def minimax(state, depth, alpha, beta, maximizing):
            current_player = player if maximizing else opponent
            if depth == 0:
                return evaluate(state, player) - evaluate(state, opponent)

            best_value = -inf if maximizing else inf
            for x, y in order:  # 中央寄りから探索
                if column_has_space(x, y):
                    make_move(state, x, y, current_player)
                    value = minimax(state, depth - 1, alpha, beta, not maximizing)
                    undo_move(state, x, y)

                    if maximizing:
                        best_value = max(best_value, value)
                        alpha = max(alpha, value)
                    else:
                        best_value = min(best_value, value)
                        beta = min(beta, value)

                    if beta <= alpha:
                        return best_value
            return best_value

        # ---- 実際の手を選ぶ ----
        best_score = -inf
        best_move = (0, 0)
        for x, y in order:
            if column_has_space(x, y):
                make_move(board, x, y, player)
                score = minimax(board, MAX_DEPTH - 1, -inf, inf, False)
                undo_move(board, x, y)
                if score > best_score:
                    best_score = score
                    best_move = (x, y)

        return best_move
