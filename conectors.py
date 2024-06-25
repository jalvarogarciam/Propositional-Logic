DEBUG = [False,False,True,False,False]

#Conectivas binarias
binary_connectors= ['&','|','>','=','<', '↚', '↛', '⊕', '↑', '↓']
all_binary_connectors= {
    '∨':'|', '+':'|', '||':'|', '|':'|',
    '∧':'&', '&&':'&', '&':'&', '*':'&',
    '→':'>','>':'>','←':'<', '<':'<',
    '↔':'=','=':'=',
    '↚':'↚', '↛':'↛', '⊕':'⊕', '↑':'↑', '↓':'↓'
}

#Conectivas unarias
unary_connectors=['!']
all_unary_connectors= {
    '¬':'!', '~':'!', '!':'!'
}

connectors = list(binary_connectors) + list (unary_connectors)
all_connectors = list(all_binary_connectors.keys()) + list (all_unary_connectors.keys())

variables = "qwertyuiopasdfghjklzxcvbnm"
def usual_to_polish(arg:list|tuple|str, counter=0)->str:
    counter += 1

    if counter == 1: arg = str(arg)

    arg = list((arg))



    if counter == 1:

        #Removes spaces
        i = 0
        while i < len(arg):
            if arg[i].isspace(): del arg[i]
            else : i+=1


        #Unify the notation and save it
        its_notation = {'!':'!','&':'&','|':'|','>':'>','=':'=','<':'<'}
        i=0
        while i < len(arg)-1:

            #unary connectors
            if arg[i] in all_unary_connectors.keys():
                its_notation[all_unary_connectors[arg[i]]] = arg[i]
                arg[i] = all_unary_connectors[arg[i]]

            #double binary connectors like &&
            elif arg[i] + arg[i+1] in all_binary_connectors.keys():
                its_notation[all_binary_connectors[arg[i] + arg[i+1]]] = arg[i] + arg[i+1]
                arg[i:i+2] = all_binary_connectors[arg[i] + arg[i+1]]

            #binary connectors like
            elif arg[i] in all_binary_connectors.keys():
                its_notation[all_binary_connectors[arg[i]]] = arg[i]
                arg[i] = all_binary_connectors[arg[i]]

            #puts missing connectors
            elif arg[i] not in ('(',')') and arg[i+1] not in ('(',')') and\
                arg[i+1] not in all_connectors :
                arg.insert(i+1,'&')
                i+=1

            i+=1


        #if it's on polish notation, return
        i = 0
        while arg[i] in all_unary_connectors.keys(): i+=1
        if arg[i] in all_binary_connectors: return "".join(arg) 


        #UNIFIES UNARY CONNECTIVES WITH PROPOSITIONS
        i = 0
        while i < len(arg):

            if arg[i] in unary_connectors and  arg[i+1] != '(':
                arg[i:i+2] = [arg[i]+arg[i+1]]
            i+=1


        #REMOVES ALL NOT(NOT(...))
        i=0
        while i+1 < len(arg):
            if (arg[i] == arg[i+1]) and arg[i] == '!':
                for x in range(2) : del arg[i]
            i+=1




    opposite = arg[0] if arg[0] in unary_connectors else ""

    expr = list(arg) if not opposite else list(arg[1:])


    #SOLVE ALL PARENTHESES
    if '(' in expr:

        i = 0
        while i < len(expr):

            if expr[i] == '(':

                #localizes the main expr between the parenthesses
                j = i
                open_par = 1
                while open_par > 0:
                    j+=1
                    if expr[j] == '(': open_par+=1
                    elif expr[j] == ')': open_par-=1

                #turns parenthesses into polish notation
                expr[i:j+1] = [usual_to_polish(expr[i+1:j], counter)]

            else: i += 1

    #FOR BINARY CONNECTIVES --> FORM P CONNTV P TO CONNTV P P
    i = 0
    while len(expr) > i+1 :
        if (expr[i] in binary_connectors):   #(prop) Cnective (prop)
            expr[i-1:i+2] = [expr[i] + expr[i-1] + expr[i+1]]   #Cnective (prop) (prop)

        else: i+=1


    if len(opposite) > 0: expr.insert(0,opposite)

    if counter == 1:
        return ("".join(expr),its_notation)
    else:
        return "".join(expr)






def test (expresion:str)-> int:
    counter=1
    for char in expresion:
        if char in binary_connectors:
            counter+=1
        elif char not in unary_connectors:
            counter-=1
    
    return counter




from math import log2



def dec_binbol(int_number:int,bits:int=None)->tuple:
        #adjust the default parameter
        if bits!=None and int_number>=2**bits:
            return None
        elif bits==None:
            bits=int(log2(int_number))+1

        binbol=[]

        #from decimal to binary
        for i in range(bits):
            binbol.insert(0,int_number%2)
            int_number//=2

        #From binary to bolean
        '''for i in range(len(binbol)):
            if binbol[i]==1 :
                binbol[i]=True
            else :
                binbol[i]=False'''
        return tuple(binbol)
