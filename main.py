from typing import List, Tuple, Optional
from math import inf
# from local_driver import Alg3D, Board  # ローカル検証用
from framework import Alg3D, Board      # 本番用


class MyAI(Alg3D):
    def get_move(
        self,
        board,  # Board でも List[List[List[int]]] でもOKにする
        player: int,
        last_move: Tuple[int, int, int]
    ) -> Tuple[int, int]:
        # -------------------------
        # 1) Board を生配列に正規化
        # -------------------------
        def as_array(b) -> List[List[List[int]]]:
            if isinstance(b, list):
                return b
            # よくある内部フィールド名を順に探す
            for attr in ("grid", "state", "board", "cells", "data"):
                v = getattr(b, attr, None)
                if isinstance(v, list):
                    return v
            # to_list() を持っていれば使う
            if hasattr(b, "to_list"):
                v = b.to_list()
                if isinstance(v, list):
                    return v
            # ここまで来たら仕様外
            raise TypeError("Unsupported Board type: expected 3D list or Board-like object")

        B = as_array(board)

        # -------------------------
        # 2) 形状を安全に取得
        #    想定は [z][y][x]（z:高さ, y:行, x:列）
        # -------------------------
        def safe_len(a) -> int:
            try:
                return len(a)
            except Exception:
                return 0

        Z = safe_len(B)
        Y = safe_len(B[0]) if Z > 0 else 0
        X = safe_len(B[0][0]) if Y > 0 else 0

        # サーバ仕様は x,y ∈ [0..3]
        BOARD_SIZE_X, BOARD_SIZE_Y = 4, 4
        BOARD_SIZE_Z = 4

        # -------------------------
        # 3) セルアクセス（範囲外は埋まり扱い）
        # -------------------------
        def cell(z: int, y: int, x: int) -> int:
            if 0 <= z < Z and 0 <= y < Y and 0 <= x < X:
                try:
                    return B[z][y][x]
                except Exception:
                    return 1
            return 1

        def column_has_space(x: int, y: int) -> bool:
            for z in range(BOARD_SIZE_Z):
                if cell(z, y, x) == 0:
                    return True
            return False

        def lowest_empty_z(x: int, y: int) -> Optional[int]:
            for z in range(BOARD_SIZE_Z):
                if cell(z, y, x) == 0:
                    return z
            return None

        def make_move(x: int, y: int, p: int) -> Optional[int]:
            z = lowest_empty_z(x, y)
            if z is not None:
                # B が十分な深さ/幅を持たない場合に備えて try
                try:
                    B[z][y][x] = p
                    return z
                except Exception:
                    return None
            return None

        def undo_move(x: int, y: int) -> None:
            # 最上段から1つ戻す（積み上げ前提）
            for z in range(BOARD_SIZE_Z - 1, -1, -1):
                if cell(z, y, x) != 0:
                    try:
                        B[z][y][x] = 0
                    except Exception:
                        pass
                    return

        # -------------------------
        # 4) 探索順（中央優先）
        # -------------------------
        def center_order():
            xs = list(range(BOARD_SIZE_X))
            ys = list(range(BOARD_SIZE_Y))
            xs = sorted(xs, key=lambda i: (abs(i - 1.5), i))
            ys = sorted(ys, key=lambda j: (abs(j - 1.5), j))
            return [(x, y) for y in ys for x in xs]

        order = center_order()
        opponent = 2 if player == 1 else 1

        # -------------------------
        # 5) 深さ（より強固・終盤6）
        # -------------------------
        empty_count = 0
        for z in range(BOARD_SIZE_Z):
            for y in range(BOARD_SIZE_Y):
                for x in range(BOARD_SIZE_X):
                    empty_count += (cell(z, y, x) == 0)

        if empty_count > 20:
            MAX_DEPTH = 4
        elif empty_count > 10:
            MAX_DEPTH = 5
        else:
            MAX_DEPTH = 6

        # -------------------------
        # 6) 勝ち判定（置いた直後の1点で判定）
        # -------------------------
        DIRS = [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (1, 1, 0), (1, 0, 1), (0, 1, 1),
            (1, 1, 1), (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (1, -1, -1), (1, 1, -1), (1, -1, 1)
        ]

        def is_winning_after(x: int, y: int, z: int, p: int) -> bool:
            if z is None:
                return False
            for dx, dy, dz in DIRS:
                cnt = 1
                for step in (1, -1):
                    nx, ny, nz = x, y, z
                    while True:
                        nx += dx * step
                        ny += dy * step
                        nz += dz * step
                        if 0 <= nx < BOARD_SIZE_X and 0 <= ny < BOARD_SIZE_Y and 0 <= nz < BOARD_SIZE_Z:
                            if cell(nz, ny, nx) == p:
                                cnt += 1
                            else:
                                break
                        else:
                            break
                if cnt >= 4:
                    return True
            return False

        # -------------------------
        # 7) 評価関数（強化版）
        # -------------------------
        def evaluate_side(p: int) -> int:
            score = 0
            for z in range(BOARD_SIZE_Z):
                for y in range(BOARD_SIZE_Y):
                    for x in range(BOARD_SIZE_X):
                        # x方向
                        if x <= BOARD_SIZE_X - 4:
                            line = [cell(z, y, x+i) for i in range(4)]
                            c, e = line.count(p), line.count(0)
                            if c == 4: return 10000
                            if c == 3 and e == 1: score += 80
                            elif c == 2 and e == 2: score += 15
                        # y方向
                        if y <= BOARD_SIZE_Y - 4:
                            line = [cell(z, y+i, x) for i in range(4)]
                            c, e = line.count(p), line.count(0)
                            if c == 4: return 10000
                            if c == 3 and e == 1: score += 80
                            elif c == 2 and e == 2: score += 15
                        # z方向
                        if z <= BOARD_SIZE_Z - 4:
                            line = [cell(z+i, y, x) for i in range(4)]
                            c, e = line.count(p), line.count(0)
                            if c == 4: return 10000
                            if c == 3 and e == 1: score += 80
                            elif c == 2 and e == 2: score += 15
                        # 3D斜め（↘↘↘）
                        if x <= BOARD_SIZE_X - 4 and y <= BOARD_SIZE_Y - 4 and z <= BOARD_SIZE_Z - 4:
                            line = [cell(z+i, y+i, x+i) for i in range(4)]
                            c, e = line.count(p), line.count(0)
                            if c == 4: return 10000
                            if c == 3 and e == 1: score += 80
                            elif c == 2 and e == 2: score += 15
                        # 他の対角線方向も評価
                        if x >= 3 and y <= BOARD_SIZE_Y - 4 and z <= BOARD_SIZE_Z - 4:
                            line = [cell(z+i, y+i, x-i) for i in range(4)]
                            c, e = line.count(p), line.count(0)
                            if c == 4: return 10000
                            if c == 3 and e == 1: score += 80
                            elif c == 2 and e == 2: score += 15
                        if x <= BOARD_SIZE_X - 4 and y >= 3 and z <= BOARD_SIZE_Z - 4:
                            line = [cell(z+i, y-i, x+i) for i in range(4)]
                            c, e = line.count(p), line.count(0)
                            if c == 4: return 10000
                            if c == 3 and e == 1: score += 80
                            elif c == 2 and e == 2: score += 15
                        if x >= 3 and y >= 3 and z <= BOARD_SIZE_Z - 4:
                            line = [cell(z+i, y-i, x-i) for i in range(4)]
                            c, e = line.count(p), line.count(0)
                            if c == 4: return 10000
                            if c == 3 and e == 1: score += 80
                            elif c == 2 and e == 2: score += 15
            return score

        def evaluate() -> int:
            # 自分 − 相手（相手3連は強減点を間接的に表現）
            me = evaluate_side(player)
            if me >= 10000:
                return 10000
            opp = evaluate_side(opponent)
            if opp >= 10000:
                return -10000
            # 相手の3連を追加で強く嫌う（近似ペナルティ）
            penalty = 0
            for z in range(BOARD_SIZE_Z):
                for y in range(BOARD_SIZE_Y):
                    for x in range(BOARD_SIZE_X):
                        if x <= BOARD_SIZE_X - 4:
                            line = [cell(z, y, x + i) for i in range(4)]
                            if line.count(opponent) == 3 and line.count(0) == 1:
                                penalty += 120
                        if y <= BOARD_SIZE_Y - 4:
                            line = [cell(z, y + i, x) for i in range(4)]
                            if line.count(opponent) == 3 and line.count(0) == 1:
                                penalty += 120
                        if z <= BOARD_SIZE_Z - 4:
                            line = [cell(z + i, y, x) for i in range(4)]
                            if line.count(opponent) == 3 and line.count(0) == 1:
                                penalty += 120
                        if x <= BOARD_SIZE_X - 4 and y <= BOARD_SIZE_Y - 4 and z <= BOARD_SIZE_Z - 4:
                            line = [cell(z + i, y + i, x + i) for i in range(4)]
                            if line.count(opponent) == 3 and line.count(0) == 1:
                                penalty += 120
            return me - opp - penalty
        # -------------------------
        # 8) Minimax + αβ（動的順序）
        # -------------------------
        def minimax(depth: int, alpha: int, beta: int, maximizing: bool) -> int:
            if depth == 0:
                return evaluate()

            current = player if maximizing else opponent

            # 候補手を評価順に並べ替え（中央寄り + 簡易スコア）
            candidates = []
            for x, y in order:
                if column_has_space(x, y):
                    z = make_move(x, y, current)
                    if z is None:
                        continue
                    val = evaluate()
                    undo_move(x, y)
                    candidates.append((val, x, y))
            candidates.sort(reverse=maximizing)

            best = -inf if maximizing else inf
            for _, x, y in candidates:
                z = make_move(x, y, current)
                if z is None:
                    continue
                val = minimax(depth - 1, alpha, beta, not maximizing)
                undo_move(x, y)

                if maximizing:
                    if val > best:
                        best = val
                    if val > alpha:
                        alpha = val
                else:
                    if val < best:
                        best = val
                    if val < beta:
                        beta = val

                if beta <= alpha:
                    break
            return int(best)

        # -------------------------
        # 9) まず即勝ち・即ブロック
        # -------------------------
        for x, y in order:
            if column_has_space(x, y):
                z = make_move(x, y, player)
                if z is not None and is_winning_after(x, y, z, player):
                    undo_move(x, y)
                    return (x, y)
                undo_move(x, y)

        for x, y in order:
            if column_has_space(x, y):
                z = make_move(x, y, opponent)
                if z is not None and is_winning_after(x, y, z, opponent):
                    undo_move(x, y)
                    return (x, y)
                undo_move(x, y)

        # -------------------------
        # 10) Minimax本探索
        # -------------------------
        best_score = -inf
        best_move = (0, 0)
        for x, y in order:
            if column_has_space(x, y):
                z = make_move(x, y, player)
                if z is None:
                    continue
                score = minimax(MAX_DEPTH - 1, -inf, inf, False)
                undo_move(x, y)
                if score > best_score:
                    best_score = score
                    best_move = (x, y)

        return best_move
