from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors, variables, notation_out
from LogicExpression import LogicExpression as le
from LogicExpression import ls
from copy import deepcopy
import time as t

start = t.time()

la = le("(a+b)")
laa = le('(c*((a*c)+b))>a')
lu = le("!a")
li = le('!b*!c*!a*!b*!c*!c*!c*!a*!c*!a')
last = [la, lu]

lsa = ls(lu, li, laa)
lso = ls(laa[1])

la = li[0]
la[0] = 'ñ'
lb = la
lic = -li

print (lic)



end = t.time()
print(end-start)

