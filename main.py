from typing import List, Tuple
import math
import copy

class MyAI:
    def __init__(self):
        self.lines = self.generate_lines()
        self.player = 0  # AI側のプレイヤー番号

    # --- 盤面に石をシミュレートして返す ---
    def simulate_move(self, board, move, player):
        x, y = move
        new_board = copy.deepcopy(board)
        for z in range(4):  # 下から順に探して置く
            if new_board[x][y][z] == 0:
                new_board[x][y][z] = player
                break
        return new_board

    # --- 次の手を選ぶ ---
    def get_move(self, board, player, last_move):
        self.player = player  # AI側のプレイヤー番号
        best_score = -math.inf
        best_move = (0, 0)

        moves = self.legal_move(board)

        # --- 序盤の中央優先ルール ---
        occupied = sum(1 for x in range(4) for y in range(4) for z in range(4) if board[x][y][z] != 0)
        if occupied < 2 and (1, 1) in moves:
            return (1, 1)

        enemy = 1 if self.player == 2 else 2

        # --- 勝ち手を即決 ---
        for move in moves:
            new_board = self.simulate_move(board, move, self.player)
            end_value, over = self.is_terminal(new_board, self.player)
            if over and end_value == 1:
                return move

        # --- 敵の勝ち手をブロック ---
        for move in moves:
            new_board = self.simulate_move(board, move, enemy)
            end_value, over = self.is_terminal(new_board, enemy)
            if over and end_value == 1:
                return move

        # --- αβ探索で評価 ---
        for move in moves:
            new_board = self.simulate_move(board, move, self.player)
            current = self.alpha_beta_minimax(
                new_board, False, 1, 3, -math.inf, math.inf,
                enemy
            )
            if current > best_score:
                best_score = current
                best_move = move

        return best_move


    # --- 勝敗判定（指定プレイヤー視点） ---
    def is_terminal(self, board, player):
        enemy = 1 if player == 2 else 2
        for line in self.lines:
            values = [board[x][y][z] for (x,y,z) in line]
            if all(val == player for val in values):
                return (1, True)
            elif all(val == enemy for val in values):
                return (-1, True)
        if all(board[x][y][z] != 0 for x in range(4) for y in range(4) for z in range(4)):
            return (0, True)
        return (0, False)

    # --- 評価関数（AI視点でスコアリング） ---
    def evaluate(self, board):
        end_value, over = self.is_terminal(board, self.player)
        if over:
            return end_value * 10000  # 1=勝ち, -1=負け, 0=引き分け

        enemy = 1 if self.player == 2 else 2
        score = 0
        for line in self.lines:
            values = [board[x][y][z] for (x,y,z) in line]
            if values.count(self.player) == 3 and values.count(0) == 1:
                score += 10
            elif values.count(self.player) == 2 and values.count(0) == 2:
                score += 1
            if values.count(enemy) == 3 and values.count(0) == 1:
                score -= 2500000
            elif values.count(enemy) == 2 and values.count(0) == 2:
                score -= 1
        return score

    def legal_move(self, board):
        action_arr = []
        for y in range(4):
            for x in range(4):
                # その列の最上段 z=3 が空いていれば合法
                if board[x][y][3] == 0:
                    action_arr.append((x, y))
        return action_arr

    # --- αβ探索 ---
    def alpha_beta_minimax(self, board, isMaximiser, depth, max_depth, alpha, beta, current_player):
        end_value, over = self.is_terminal(board, current_player)
        if over or depth == max_depth:
            return self.evaluate(board)

        if isMaximiser:
            max_eval = -math.inf
            for move in self.legal_move(board):
                new_board = self.simulate_move(board, move, current_player)
                next_player = 1 if current_player == 2 else 2
                eval = self.alpha_beta_minimax(new_board, False, depth + 1, max_depth, alpha, beta, next_player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            next_player = 1 if current_player == 2 else 2
            for move in self.legal_move(board):
                new_board = self.simulate_move(board, move, current_player)
                eval = self.alpha_beta_minimax(new_board, True, depth + 1, max_depth, alpha, beta, next_player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    # --- 勝ち筋ラインを事前生成 ---
    def generate_lines(self):
        lines = []
        rng = range(4)
        # 直線
        for z in rng:
            for y in rng:
                lines.append([(x, y, z) for x in rng])
            for x in rng:
                lines.append([(x, y, z) for y in rng])
        for y in rng:
            for x in rng:
                lines.append([(x, y, z) for z in rng])
        # 平面斜め
        for z in rng:
            lines.append([(i, i, z) for i in rng])
            lines.append([(i, 3 - i, z) for i in rng])
        for y in rng:
            lines.append([(i, y, i) for i in rng])
            lines.append([(i, y, 3 - i) for i in rng])
        for x in rng:
            lines.append([(x, i, i) for i in rng])
            lines.append([(x, i, 3 - i) for i in rng])
        # 3D斜め
        lines.append([(i, i, i) for i in rng])
        lines.append([(i, i, 3 - i) for i in rng])
        lines.append([(i, 3 - i, i) for i in rng])
        lines.append([(3 - i, i, i) for i in rng])
        return lines
