from typing import List, Tuple
#from local_driver import Alg3D, Board # ローカル検証用
# from framework import Alg3D, Board # 本番用
import math

class MyAI():
    def __init__(self):
        # all possible winning lines
        self.lines = self.generate_lines()
        # check if the game is over
        self.over = False
        self.player = 0
        self.end_value = 0 # 1 if win -1 if lose 0 if
    
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # ここにアルゴリズムを書く
        self.player = player
        # HERE OPTIMISE
        best_score = 0
        best_move = (0, 0)
        print("Legal moves :", self.legal_move(board))
        for action in self.legal_move(board):
            print("Action :", action)
            # if winning move, play it
            new_board = self.result(board, action)
            if self.is_terminal(new_board) and self.end_value == 1:
                return (action[1], action[2])
            current = self.alpha_beta_minimax(board, False, 0, 3, alpha=-math.inf, beta=math.inf)
            if current > best_score:
                best_score = current
                best_move = (action[1], action[2])
        return best_move

    def result(self, board, action):
        """
            return the board that result from a move
            board: current board
            move: (z,y,x) where to play
            player: which player is playing
            return new board
        """ 
        # 元のボードをコピーして変更
        import copy
        new_board = copy.deepcopy(board)
        new_board[action[0]][action[1]][action[2]] = self.player
        return new_board

    def generate_lines(self):
        lines = []
        rng = range(4)
        
        # 縦、横、奥行きの直線
        for z in rng:
            for y in rng:
                lines.append([(z,y,x) for x in rng])  # X軸方向
            for x in rng:
                lines.append([(z,y,x) for y in rng])  # Y軸方向
        for y in rng:
            for x in rng:
                lines.append([(z,y,x) for z in rng])  # Z軸方向

        # 平面の斜め
        for z in rng:
            lines.append([(z,i,i) for i in rng])      # 対角線1
            lines.append([(z,i,3-i) for i in rng])    # 対角線2
        for y in rng:
            lines.append([(i,y,i) for i in rng])      # ZX平面対角線1
            lines.append([(i,y,3-i) for i in rng])    # ZX平面対角線2
        for x in rng:
            lines.append([(i,i,x) for i in rng])      # ZY平面対角線1
            lines.append([(i,3-i,x) for i in rng])    # ZY平面対角線2

        # 3D対角線
        lines.append([(i,i,i) for i in rng])
        lines.append([(i,i,3-i) for i in rng])
        lines.append([(i,3-i,i) for i in rng])
        lines.append([(3-i,i,i) for i in rng])
        
        return lines

    def is_terminal(self, board):
        """
            check if the game ended
            return True if game is over, False otherwise
        """
        enemy = 1 if self.player == 2 else 2
        self.over = False
        self.end_value = 0
        
        for line in self.lines:
            values = [board[z][y][x] for (z,y,x) in line]
            if all(val == self.player for val in values):
                self.over = True
                self.end_value = 1
                return True
            elif all(val == enemy for val in values):
                self.over = True
                self.end_value = -1
                return True
        
        # ボードが満杯かチェック
        if all(board[3][y][x] != 0 for x in range(4) for y in range(4)):
            self.over = True
            self.end_value = 0
            return True
        
        return False

    def evaluate(self, board):
        """
            END CONDITION
            return 100 if ai win -100 if lose and 0 equal
        """
        enemy = 1 if self.player == 2 else 2
        score = 0

        if self.over:
            return self.end_value * 100
		# Heuristic scoring
        for line in self.lines:
			# Example line : [(0,0,0), (1,1,1), (2,2,2), (3,3,3)]
			# Example values : [-1, 1, 0, 2]
            values = [board[x][y][z] for (x,y,z) in line]
			
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
            use to determine how many legal moves are possible
        """
        action_arr = []

        for plane_i in range(4):
            print("Plane i :", plane_i)
            for row_i in range(4):
                print("Row i :", row_i)
                for space_i in range(4):
                    if board[plane_i][row_i][space_i] == 0 \
                        and (3 == plane_i \
                        or board[plane_i + 1][row_i][space_i] == 0 ):

                        action_arr.append((plane_i, row_i, space_i))
        return action_arr

    def alpha_beta_minimax(self, board, isMaximiser, depth, max_depth, alpha, beta):
        """
            isMaximiser: is the computer turn to check in the three
            depth: how far in the three you are
            max_deth: maximmum depth
        """
        if self.is_terminal(board) or depth == max_depth:
            return self.evaluate(board)

        if isMaximiser:
            max_eval = -math.inf
            for action in self.legal_move(board):
                eval = self.alpha_beta_minimax(self.result(board, action), False, depth + 1, max_depth, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for action in self.legal_move(board):
                eval = self.alpha_beta_minimax(self.result(board, action), True, depth + 1, max_depth, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval



