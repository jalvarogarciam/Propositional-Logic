from LogicExpression import LogicExpression



cadena = "a+b"

expr1 = LogicExpression("(a+b+c+d*g) = 0 = 1 = 2")
expr2 = LogicExpression(20)
lista = []
expr2.find_vars()
print (expr2.vars)


