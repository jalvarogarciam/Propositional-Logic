from LogicExpression import LogicExpression as le
from copy import deepcopy


la = le("a|b")

print((la()[1][0]))