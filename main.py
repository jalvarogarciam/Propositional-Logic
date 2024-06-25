from LogicExpression import LogicExpression
from copy import deepcopy

le = LogicExpression("b ↚  c")
la = LogicExpression("a*(!b)")
#lu = LogicExpression("(abc) + (ab) + (a+c)")
print(le)
