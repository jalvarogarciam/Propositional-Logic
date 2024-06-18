from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors


class LogicExpression:
    '''
    The shape of LogicExpression's are like a "tree of expression". But, the main
    type is a Unary or Binary Connective. 

    ex:CONNECTIVE(CONNECTIVE(CONNECTIVE(...),CONNECTIVE(...))) on his leafs, we can
    found bool vars x,y,z...

    And then, it will be able to evaluate the expression with a __call__.
    '''
    ##########################################################################
    def __init__(self, arg:str, root:"LogicExpression" = None, counter=0):
        self.counter = counter + 1     #strange things about recursibity

        self.root = root if type(root) != type(None) else self

        self.notation = {'!':'!','&':'&','|':'|','>':'>','=':'=','<':'<'}

        self.__argument : LogicExpression|str|bool|int
        self.vars: dict = {}
        self.type: str

        self.__clausular_set = set("empty")


        if type(arg) == str: 

            if len(arg) > 1 : self.expr__init__(arg)
            elif arg.isdigit() : self.bool__init__(int(arg))
            else: self.proposition__init__(arg)


        elif type(arg) in (bool,int): self.bool__init__(arg)

        #type(arg) in (AND,OR,IMPLY,BICOND):
        elif type(arg) in (tuple,list) : self.connective__init__(arg)

        elif type(arg) == LogicExpression : self.copy__init__(arg)

        self.find_vars()

    ##########################################################################
    #Expression builder
    def expr__init__(self, raw_expression:str|list|tuple):

        if self.counter == 1:

            raw_expression, self.notation = usual_to_polish(raw_expression)

        self.type = raw_expression[0]


        #BUILDS A NEW L.E. FOR ARGUMENT######################################
        
        #UNARY CONNECTIVES (!)
        if self.type in unary_connectors:

            self.__argument = LogicExpression(raw_expression[1:], self, self.counter)

        #BINARY CONNECTIVES (|,&,<,>,=)
        else:   # self.type in binary_connectors:

            #LOCATES the range of the main connective
            #It's the same algorithm that we use to check if a polish expr is correct
            in_range,i = 1,1
            while in_range != 0 :
                if raw_expression[i] in binary_connectors: 
                    in_range+=1
                    
                elif raw_expression[i] not in unary_connectors: in_range-=1
                i+=1

            #ARGUMENT BUILDINT
            self.__argument = [LogicExpression(raw_expression[1:i], self, self.counter), \
                                LogicExpression(raw_expression[i:], self, self.counter)]

            #ASOCIATIVE PROPERTY
            self.asociate()

            #REDUCES EACH < TO A >
            if self.type == '<':
                self.type = '>'
                self[0], self[1] = self[1], self[0]

            #simplify 0's and 1's
            self.check_neutral_and_dominant()

    ##########################################################################
    #Proposition builder
    def proposition__init__(self, proposition:str|list|tuple):

        self.__argument = str(proposition[0])    #always is a char
        self.vars = {proposition[0]:0}
        self.type = 'p'

    ##########################################################################
    #Bool builder
    def bool__init__(self, true:bool|int):

        self.__argument = bool(true)
        self.type = '1' if bool(true) else '0'

    ##########################################################################
    #Copy Builder
    def copy__init__(self, other: 'LogicExpression'):
        self.counter = 1

        self.type = other.type

        self.notation = other.notation

        self.vars = other.vars.copy()

        if other.type in binary_connectors:
            self.__argument = other.__argument.copy()
        elif other.type in unary_connectors:
            self.__argument = LogicExpression(other.__argument, self, self.counter)
        else:
            self.__argument = other.__argument

    ##########################################################################
    #connective Builder (list)
    def connective__init__(self,le_list:list|tuple):
        self.type = le_list[0]
        self.__argument = []

        if self.type in unary_connectors: 
            self.__argument = LogicExpression(le_list[1])
        
        else: #self.type in binary_connectors:
            for le in le_list[1:]:   self.__argument.append(LogicExpression(le))

    ##########################################################################
    ##########################################################################

    def find_vars(self):
        self.vars = dict({})
        leafs = [] 
        self.get_leafs(leafs)

        for leaf in leafs:
            if leaf[0] not in self.vars:    self.vars[leaf[0]] = 0

    def get_leafs(self, leafs:list=[])->list['LogicExpression']:
        if self.type == 'p':    leafs.append(self)
        elif self.type in connectors:
            for i in range (len(self)):
                self[i].get_leafs(leafs)

    ###########################################################################
    #OPERATORS
    ###########################################################################
    #Arithmetic operators
    def __add__(self, other) ->'LogicExpression':
        return LogicExpression(['|', self, other])
    def __or__(self, other) ->'LogicExpression': return self + other
    
    def __mul__(self, other) ->'LogicExpression':
        return LogicExpression(['&', self, other])
    def __and__(self, other) ->'LogicExpression': return self * other

    def __xor__(self, other) ->'LogicExpression':
        return (-self * (other)) + (self * (-other))

    def __sub__(self, other) ->'LogicExpression': return self * -(self*other)

    def __neg__(self) ->'LogicExpression':
        return LogicExpression(['!', self])
    def __invert__(self) ->'LogicExpression': return - self

    #Relational operators
    def __eq__ (self, other)->bool:
        return self.minterms() == other.minterms()
    def __ne__ (self, other)->bool:
        return not self == other
    def __le__ (self, other)->bool:
        return self in other
    def __ge__ (self, other)->bool:
        return other in self
    def __lt__ (self, other)->bool:
        return not self >= other
    def __gt__ (self, other)->bool:
        return not self <= other
    def __contains__(self, other)->bool:
        return self.minterms().issuperset(other.minterms())
    

    def istautology(self)->bool:
        return len(self.maxterms()) == 0
    def iscontradiction(self)->bool:
        return len(self.minterms()) == 0
    def issatisfacible(self)->bool:
        return not self.iscontradiction()
    def isrefutable(self)->bool:
        return not self.istautology()
    def iscontingent(self)->bool:
        return self.isrefutable() and self.issatisfacible()

    def __len__(self)->int:
    
        if self.type in binary_connectors:
            return len(self.__argument) #it's a list
        
        else: return 1

    ########Items
    def __getitem__(self,index:int)->'LogicExpression': 

        if index < 0:
            the_root = self.root
            i = -1
            while i > index and the_root != the_root.root: 
                the_root = the_root.root
                i-=1
            return the_root

        else:
            if len(self) == 1 : return (self.__argument)
            else : return self.__argument[index]

    def __setitem__(self, index, value):
        if len(self) == 1 : self.__argument = LogicExpression(value)
        else : self.__argument[index] = LogicExpression(value)

    def __delitem__(self,index):
        if len(self) == 1 : del self.__argument
        else : del self.__argument[index]
    ##########################################################################
    ###########################################################################


    #Main propperties##########################################################
    def check_neutral_and_dominant(self):
        i=0
        while i < (len(self)):

            if self[i].type == ('0'):

                if self.type == '|': 
                    del self[i]
                    if len(self) == 1: self.copy__init__(self.__argument[0])

                elif self.type == '&':
                    self.bool__init__(0)
                
                elif self.type == '>' and i==0:
                    self.bool__init__(1)

            elif self[i].type == ('1'):

                if self.type == '&': 
                    del self[i]
                    if len(self) == 1: self.copy__init__(self.__argument[0])

                elif self.type == '|':
                    self.bool__init__(1)
            i+=1

    def asociate(self):
        if self.type not in ('|','&'): return None

        term_index = 0

        for x in range(len(self)):

            if self[term_index].type == self.type:

                lenght = len(self[term_index])

                i = lenght - 1
                while i >= 0:
                    self.__argument.insert(term_index+1, self[term_index][i])
                    i-=1
                del self[term_index]
                term_index += lenght
        
            else: term_index += 1
    ###########################################################################



    #Truth values#############################################################
    def __call__(self,vars={})->bool:
        truth : bool = False

        if vars == {}: return self.truth_board()

        #Basics
        if self.type == 'p': truth = bool(vars[self.__argument])

        elif self.type in ('0','1'): truth = bool(self.__argument)

        #Recursivity
        elif self.type == '!': truth = not bool(self.__argument(vars))

        elif self.type in binary_connectors:

            truth_list:list = self.__argument.copy()

            #TURNS each argument INTO A BOOL VALUE
            #operator __call__ -> evaluate
            for i in range(len(truth_list)): truth_list[i] = truth_list[i](vars)

            if self.type == '&':
                truth = True
                for i in range(len(truth_list)): truth &= truth_list[i]

            elif self.type == '|':
                truth = False
                for i in range(len(truth_list)): truth |= truth_list[i]

            elif self.type == '>':
                truth = (not truth_list[0]) or truth_list[1]

            elif self.type == '=':
                truth = ((not truth_list[0]) or truth_list[1]) and \
                ((not truth_list[1]) or truth_list[0])

        return (1 if truth else 0)


    def truth_board(self)->tuple:

        if len(self.vars) == 0: self.find_vars()

        board = []


        values = dict({})
        for v in self.vars.keys(): values.update({v:0})

        num_vars = len(self.vars)

        if self.type in ('1','0'):
            board.append([self.type, bool(int(self.type))])

        else:
            for bit in range(2**num_vars):
                bits = dec_binbol(bit,num_vars)
                i = 0
                board.append([[]])
                for k in values.keys():
                    values[k]=bits[i]
                    board[bit][0].append(str(int(bits[i])))
                    i+=1
                board[bit].append(str(bool(self(values))))

        return (self.vars.keys(), board)

    ###########################################################################

    def to_canonical_shape(self,on_minterms=True)->'LogicExpression':

        if len(self.vars) == 0: self.find_vars()
        
        if self.type.isdigit(): return LogicExpression(self)
        num_vars = len(self.vars.keys())
        minterms = tuple(self.minterms())
        maxterms = tuple(set(range(2**num_vars)) - set(minterms))

        terms = minterms if on_minterms else maxterms

        symbol = '&' if on_minterms else '|'

        vars = list(self.vars.keys())
        le_list = []
        for i in terms:
            binary = dec_binbol(i,num_vars)

            string = ""
            i=0
            if on_minterms:
                for bit in binary:
                    oposite = '!' if not bit else ''
                    string += oposite + vars[i] + symbol
                    i += 1
            else:
                for bit in binary:
                    oposite = '!' if bit else ''
                    string += oposite + vars[i] + symbol
                    i += 1

            string = '('+string[:-1]+')'

            le_list.append(LogicExpression(string))

        symbol = '&' if symbol=='|' else '|'
        le_list.insert(0,symbol)

        copy = LogicExpression(le_list) if len(le_list) > 1 else LogicExpression(str(self))

        return copy


    # Minterms / Maxterms######################################################
    def minterms(self)->set: return self.canonical_terms(True)
    def maxterms(self)->set: return self.canonical_terms(False)
    def canonical_terms(self,on_minterms=True):

        if len(self.vars) == 0: self.find_vars()

        terms = []

        values = dict({})
        for v in self.vars.keys(): values.update({v:0})

        num_vars = len(self.vars.keys())

        for bit in range(2**num_vars):

            bits = dec_binbol(bit,num_vars)

            i = 0
            for k in values.keys():
                values[k]=bits[i]
                i+=1

            if on_minterms:
                if self(values): terms.append(bit)
            else: 
                if not self(values): terms.append(bit)
        
        return set(terms)
    ###########################################################################



    #CASTING##################################################################
    def __bool__(self)->bool:
        return self.istautology()
    
    def __str__(self)->str:

        string = ""


        if self.type in binary_connectors:
        
            for i in range(len(self)):

                string += str(self[i]) + ' ' + self.type + ' '

            string = '(' + string[:-3] + ')' # adds () and removes the last connective
            

        if self.type in unary_connectors:
        
            if self.__argument.type == 'p':
                string += self.type + str(self.__argument)
        
            elif self.__argument.type in ('0','1'): 
                string+= str(int(not bool(self[0][0])))

            elif len(self.__argument) > 1:
                string += self.type + '(' + str(self.__argument) + ')'
        
        elif self.type in ('p','0','1'):
            string += self.__argument if self.type == 'p' else \
                        str(int(self.__argument))


        #TURNS CONNECTIVES IN ITS INITIAL NOTATION
        if self.counter == 1 and type(self.__argument) not in (str, bool, int):
            string = list(string)

            for i in range(len(string)):

                if string[i] in self.notation.keys():
                    string[i] = self.notation[string[i]]

            string = string[1:-1]   #DELETE PARENTHESES (...)

            string = "".join(string)

        return string
    ##########################################################################


