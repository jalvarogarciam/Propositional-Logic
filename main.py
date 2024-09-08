from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors, variables, notation_out
from LogicExpression import LogicExpression as le
from LogicExpression import ls
from copy import deepcopy
import time as t

start = t.time()

la = le("(a+b)")
laa = le('a*(a+(b+(c>(e=(c+b+(a*!a*!b*!c))))))')
lu = le("!a")
li = le('!a*!b*!c')
last = [la, lu]

print(lu in li)



end = t.time()
print(end-start)







