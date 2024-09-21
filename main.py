from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors, variables, notation_out
from LogicExpression import LogicExpression as le
from LogicExpression import ls
from copy import deepcopy
import time as t

start = t.time()

la = le('a+b')
li = le('c+b')
lu = le('r')

lx = le('(a ∨ b) ∧ (c ∨ b) ∧ r')

print(bool(not set({1})))


la = le('a*b')

print(lx.to_canonical_shape(False))




end = t.time()
print(end-start)

