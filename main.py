from LogicExpression import LogicExpression



le = LogicExpression("abc")

vars, board = le ()

print ("".join(board[0][0]))
