from typing import List, Tuple
import math
import copy

class MyAI:
    def __init__(self):
        self.lines = self.generate_lines()
        self.player = 0

    def get_move(self, board, player, last_move):
        self.player = player
        best_score = -math.inf
        best_move = (0, 0)

        for action in self.legal_move(board):
            new_board = self.result(board, action)

            # 勝ち筋なら即決
            end_value, over = self.is_terminal(new_board)
            if over and end_value == 1:
                return (action[2], action[1])

            # αβ探索
            current = self.alpha_beta_minimax(new_board, False, 1, 3, -math.inf, math.inf)


            if current > best_score:
                best_score = current
                best_move = (action[2], action[1])

        return best_move


    def result(self, board, action):
        new_board = copy.deepcopy(board)
        new_board[action[0]][action[1]][action[2]] = self.player
        return new_board

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

        # 平面の斜め
        for z in rng:
            lines.append([(i, i, z) for i in rng])
            lines.append([(i, 3 - i, z) for i in rng])
        for y in rng:
            lines.append([(i, y, i) for i in rng])
            lines.append([(i, y, 3 - i) for i in rng])
        for x in rng:
            lines.append([(x, i, i) for i in rng])
            lines.append([(x, i, 3 - i) for i in rng])

        # 3D 対角線
        lines.append([(i, i, i) for i in rng])
        lines.append([(i, i, 3 - i) for i in rng])
        lines.append([(i, 3 - i, i) for i in rng])
        lines.append([(3 - i, i, i) for i in rng])

        return lines

    def is_terminal(self, board):
        enemy = 1 if self.player == 2 else 2

        for line in self.lines:
            values = [board[x][y][z] for (x, y, z) in line]
            if all(val == self.player for val in values):
                return (1, True)
            elif all(val == enemy for val in values):
                return (-1, True)

        # 全セル埋まっていたら引き分け
        if all(board[x][y][z] != 0 for x in range(4) for y in range(4) for z in range(4)):
            return (0, True)

        return (0, False)

    def evaluate(self, board):
        end_value, over = self.is_terminal(board)
        if over:
            return end_value * 10000  # 終局は最優先

        enemy = 1 if self.player == 2 else 2
        score = 0

        for line in self.lines:
            values = [board[x][y][z] for (x, y, z) in line]

            # 自分の勝ち筋
            if values.count(self.player) == 3 and values.count(0) == 1:
                score += 500
            elif values.count(self.player) == 2 and values.count(0) == 2:
                score += 10

            # 相手の勝ち筋
            if values.count(enemy) == 3 and values.count(0) == 1:
                score -= 1000
            elif values.count(enemy) == 2 and values.count(0) == 2:
                score -= 50

        # --- 中心ボーナス ---
        center_coords = [(1,1), (1,2), (2,1), (2,2)]
        for z in range(4):
            for (cx, cy) in center_coords:
                if board[cx][cy][z] == self.player:
                    score += 30   # 中心マスは強く評価
                elif board[cx][cy][z] == enemy:
                    score -= 20   # 相手が取ってると不利

        return score

    def legal_move(self, board):
        action_arr = []
        for plane_i in range(4):
            for row_i in range(4):
                for space_i in range(4):
                    if board[plane_i][row_i][space_i] == 0 and (
                        plane_i == 0 or board[plane_i - 1][row_i][space_i] != 0
                    ):
                        action_arr.append((plane_i, row_i, space_i))
        return action_arr

    def alpha_beta_minimax(self, board, isMaximiser, depth, max_depth, alpha, beta):
        end_value, over = self.is_terminal(board)
        if over or depth == max_depth:
            return self.evaluate(board)

        if isMaximiser:
            max_eval = -math.inf
            for action in self.legal_move(board):
                eval = self.alpha_beta_minimax(
                    self.result(board, action), False, depth + 1, max_depth, alpha, beta
                )
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for action in self.legal_move(board):
                eval = self.alpha_beta_minimax(
                    self.result(board, action), True, depth + 1, max_depth, alpha, beta
                )
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
