from LogicExpression import LogicExpression
from copy import deepcopy

le = LogicExpression("a<(b&c)")
la = LogicExpression("a*(!b)")
lu = LogicExpression("(abc) + (ab) + (a+c)")
new_vars = ({'a':'b', 'b':'a', 'c':'z'})
lea = le + la
lea2 = deepcopy(lea)
print(lea2)
print(la.vars, le.vars)
print(lea.minterms(), lea)
lea.order(*('a', 'b', 'c'))
print(lea.vars)
