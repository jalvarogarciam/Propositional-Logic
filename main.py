from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors, variables, notation_out
from LogicExpression import LogicExpression as le
from LogicExpression import ls
from copy import deepcopy
import time as t

start = t.time()

la = le('a')
lx = le("a+!(b=(!p))").copy(mode='i')
lx.append(la)
print(lx.copy())



print(lx)

end = t.time()
print(end-start)

