from typing import List, Tuple
import math
import copy

class MyAI():
    def __init__(self):
        # 勝利判定用ラインの生成
        self.lines = self.generate_lines()
        self.player = 0

    def get_move(
        self,
        board: List[List[List[int]]],
        player: int,
        last_move: Tuple[int, int, int]
    ) -> Tuple[int, int]:
        try:
            self.player = player
            best_score = -math.inf
            best_move = None

            moves = self.legal_move(board)
            if not moves:  # 合法手がない場合
                return (0, 0)

            for action in moves:
                new_board = self.result(board, action)

                # 勝ち筋なら即決
                if self.is_terminal(new_board)[0] == 1:
                    return (action[1], action[2])

                # 敵の勝ち筋をブロックする手を検出
                enemy_player = 1 if self.player == 2 else 2
                enemy_board = copy.deepcopy(board)
                enemy_board[action[0]][action[1]][action[2]] = enemy_player
                original_player = self.player
                self.player = enemy_player
                if self.is_terminal(enemy_board)[0] == 1:
                    self.player = original_player
                    return (action[1], action[2])  # ブロック手
                self.player = original_player

                # αβ探索（深度を2に下げて安全性向上）
                current = self.alpha_beta_minimax(
                    new_board,
                    False,   # 次は相手
                    1,       # 1手目から
                    2,       # 最大深さを3→2に変更
                    alpha=-math.inf,
                    beta=math.inf
                )

                if current > best_score:
                    best_score = current
                    best_move = (action[1], action[2])

            # 安全な手を返す
            if best_move is not None:
                # 返す前に座標が有効かダブルチェック
                y, x = best_move
                if 0 <= y <= 3 and 0 <= x <= 3:
                    return best_move
            
            if moves:
                # フォールバック: 最初の合法手
                action = moves[0]
                return (action[1], action[2])
            else:
                return (0, 0)
                
        except Exception as e:
            # エラー時のフォールバック
            moves = self.legal_move(board)
            if moves:
                action = moves[0]
                return (action[1], action[2])
            return (0, 0)

    def result(self, board, action):
        new_board = copy.deepcopy(board)
        new_board[action[0]][action[1]][action[2]] = self.player
        return new_board

    def generate_lines(self):
        lines = []
        rng = range(4)

        # 各軸方向
        for z in rng:
            for y in rng:
                lines.append([(z, y, x) for x in rng])  # X方向
            for x in rng:
                lines.append([(z, y, x) for y in rng])  # Y方向
        for y in rng:
            for x in rng:
                lines.append([(z, y, x) for z in rng])  # Z方向

        # 平面対角線
        for z in rng:
            lines.append([(z, i, i) for i in rng])
            lines.append([(z, i, 3 - i) for i in rng])
        for y in rng:
            lines.append([(i, y, i) for i in rng])
            lines.append([(i, y, 3 - i) for i in rng])
        for x in rng:
            lines.append([(i, i, x) for i in rng])
            lines.append([(i, 3 - i, x) for i in rng])

        # 3D対角線
        lines.append([(i, i, i) for i in rng])
        lines.append([(i, i, 3 - i) for i in rng])
        lines.append([(i, 3 - i, i) for i in rng])
        lines.append([(3 - i, i, i) for i in rng])

        return lines

    def is_terminal(self, board):
        """
        戦局判定: (end_value, is_over)
        end_value = 1 (勝ち), -1 (負け), 0 (引分/未終局)
        """
        enemy = 1 if self.player == 2 else 2

        for line in self.lines:
            values = [board[z][y][x] for (z, y, x) in line]
            if all(val == self.player for val in values):
                return (1, True)
            elif all(val == enemy for val in values):
                return (-1, True)

        # 盤面フル
        if all(board[z][y][x] != 0 for z in range(4) for y in range(4) for x in range(4)):
            return (0, True)

        return (0, False)

    def evaluate(self, board):
        """
        評価関数
        """
        end_value, over = self.is_terminal(board)
        if over:
            return end_value * 100

        enemy = 1 if self.player == 2 else 2
        score = 0

        for line in self.lines:
            values = [board[z][y][x] for (z, y, x) in line]

            if values.count(self.player) == 3 and values.count(0) == 1:
                score += 10
            elif values.count(self.player) == 2 and values.count(0) == 2:
                score += 1

            if values.count(enemy) == 3 and values.count(0) == 1:
                score -= 10
            elif values.count(enemy) == 2 and values.count(0) == 2:
                score -= 1

        return score

    def legal_move(self, board):
        """
        合法手生成 (下に支えがある or 最下段のみ)
        """
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
        if depth == max_depth or self.is_terminal(board)[1]:
            return self.evaluate(board)

        if isMaximiser:
            max_eval = -math.inf
            legal_actions = self.legal_move(board)
            if not legal_actions:
                return self.evaluate(board)
            
            for action in legal_actions:
                new_board = self.result(board, action)
                eval = self.alpha_beta_minimax(new_board, False, depth + 1, max_depth, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            legal_actions = self.legal_move(board)
            if not legal_actions:
                return self.evaluate(board)
                
            # 敵のプレイヤーの手をシミュレート
            enemy_player = 1 if self.player == 2 else 2
            original_player = self.player
            
            for action in legal_actions:
                # 敵の手を作成
                new_board = copy.deepcopy(board)
                new_board[action[0]][action[1]][action[2]] = enemy_player
                
                # 一時的に敵プレイヤーに切り替え
                self.player = enemy_player
                eval = self.alpha_beta_minimax(new_board, True, depth + 1, max_depth, alpha, beta)
                self.player = original_player  # プレイヤーを復元
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            
            return min_eval
