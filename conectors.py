DEBUG = [False,False,True,False,False]

#Conectivas binarias
binary_connectors= ['*','+','>','=','<', '↚', '↛', '⊕', '↑', '↓']
all_binary_connectors= {
    '∨':'+', '+':'+', '|':'+',
    '∧':'*', '&':'*', '*':'*',
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

notation_out = {'!':'¬', '*':'∧', '+':'∨','>':'→','=':'↔','<':'←', '↚':'↚', '↛':'↛', '⊕':'⊕', '↑':'↑', '↓':'↓'}
notation_in = {value:key for key, value in notation_out.items()}
variables = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"



def usual_to_polish(arg:str)->str:

    first_time = False

    if type(arg) == str:
        first_time = True

        # Removes spaces
        arg = arg.replace(" ", "")

        # replacements dictionary
        replacements = {**all_unary_connectors, **all_binary_connectors}

        # makes the translation board with
        translation_board = str.maketrans(replacements)

        # replaces the connectors
        arg = arg.translate(translation_board)

        # Manejar conectores binarios dobles como &&
        arg = arg.replace("&&", "&")
        arg = arg.replace("||", "|")


        arg = list(arg)
        i=0
        while i < len(arg)-1:
            #puts missing connectors
            if arg[i].isalpha() and arg[i+1] not in ('(',')') and\
            arg[i+1] not in all_connectors :
                arg.insert(i+1,'*')
                i+=1

            i+=1

        #unifies unary connectives with propositions
        i = 0
        while i < len(arg):
            if arg[i] == '!' and  arg[i+1] != '(':
                arg[i:i+2] = [arg[i]+arg[i+1]]
            i+=1


    #SOLVE ALL PARENTHESES
    if '(' in arg:

        i = 0
        while i < len(arg):

            if arg[i] == '(':
                
                #localizes the main expr between the parenthesses
                j = i
                open_par = 1
                while open_par > 0:
                    j+=1
                    if arg[j] == '(': open_par+=1
                    elif arg[j] == ')': open_par-=1

                #turns parenthesses into polish notation
                if arg[i-1] != '!':
                    arg[i:j+1] = usual_to_polish(arg[i+1:j])
                else:
                    arg[i-1:j+1] = ['!' + usual_to_polish(arg[i+1:j])[0]]

            else: i += 1

    
    #FOR BINARY CONNECTIVES --> FORM P CONNTV P TO CONNTV P P
    i = 0
    while len(arg) > i+1 :

        if (arg[i] in binary_connectors):   #(prop) Cnective (prop)
            arg[i-1:i+2] = [arg[i] + arg[i-1] + arg[i+1]]   #Cnective (prop) (prop)

        else: i+=1

    return "".join(arg) if first_time else arg






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


