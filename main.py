from LogicExpression import LogicExpression
from copy import deepcopy

le = LogicExpression("(ac) + (ab) + (abc) + (ac)")
#la = LogicExpression("(abc) + (ab) + (ac)")
#lu = LogicExpression("(abc) + (ab) + (a+c)")
print(le.vars)
le.change_vars(['x', 'y', 'z'])
print(le)
