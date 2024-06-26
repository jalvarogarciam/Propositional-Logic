from LogicExpression import LogicExpression
from copy import deepcopy

le = LogicExpression("a⊕(b&c)", order=('c', 'b', 'a'))
la = LogicExpression("a*(!b)")
lu = LogicExpression("(abc) + (ab) + (a+c)")
new_vars = ({'a':'b', 'b':'a', 'c':'z'})
lea = le +la
print(lea.minterms(), lea)
lea.order(*('a', 'b', 'c'))
lea.unify(la)
print(LogicExpression("ab") == LogicExpression("xa"))
print(le)
