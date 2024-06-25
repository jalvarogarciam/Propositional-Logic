from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors, variables


from copy import deepcopy
import random

class LogicExpression:
    '''
    The shape of LogicExpression's are like a "tree of expression". But, the main
    type is a Unary or Binary Connective. 

    ex:CONNECTIVE(CONNECTIVE(CONNECTIVE(...),CONNECTIVE(...))) on his leafs, we can
    found bool vars x,y,z...

    And then, it will be able to evaluate the expression with a __call__.
    '''
    ##########################################################################
    def __init__(self, arg:str = 0, root:"LogicExpression" = None):

        self.root = root if type(root) != type(None) else self

        self.notation = {'!':'!','&':'&','|':'|','>':'>','=':'=','<':'<'}

        self.__argument : LogicExpression|str|bool|int
        self.vars: dict = {}
        self.type: str


        if type(arg) == str: 

            if len(arg) > 1 : self.expr__init__(arg)
            elif arg.isdigit() : self.bool__init__(int(arg))
            else: self.proposition__init__(arg)


        elif type(arg) in (bool,int): self.bool__init__(arg)

        elif type(arg) in (tuple,list) : self.connective__init__(arg)

        elif type(arg) == LogicExpression : self.copy__init__(arg)

        self.find_vars()

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
    #Expression builder
    def expr__init__(self, raw_expression:str|list|tuple):

        if self.root is self:

            raw_expression, self.notation = usual_to_polish(raw_expression)

        self.type = raw_expression[0]


        #BUILDS A NEW L.E. FOR ARGUMENT######################################
        
        #UNARY CONNECTIVES (!)
        if self.type in unary_connectors:

            self.__argument = LogicExpression(raw_expression[1:], self)

        #BINARY CONNECTIVES (|,&,<,>,=)
        else:   # self.type in binary_connectors:

            #LOCATES the range of the main connective
            #It's the same algorithm that we use to check if a polish expr is correct
            in_range,i = 1,1
            while in_range != 0 :
                if raw_expression[i] in binary_connectors: in_range+=1

                elif raw_expression[i] not in unary_connectors: in_range-=1

                i+=1

            #ARGUMENT BUILDING
            self.__argument = [LogicExpression(raw_expression[1:i], self), \
                                LogicExpression(raw_expression[i:], self)]

            if self.type in ('↚', '↛', '⊕', '↑', '↓'):

                if self.type == '⊕':
                    self.copy(- LogicExpression(['=', self[0], self[1]]))

                elif self.type == '↛':
                    self.copy( - LogicExpression(['>',self[0], self[1]]))

                elif self.type == '↚':
                    self.copy( - LogicExpression(['>',self[1], self[0]]))

                elif self.type == '↑':
                    self.copy( - LogicExpression(['&',self[0], self[1]]))

                elif self.type == '↓':
                    self.copy( - LogicExpression(['|',self[0], self[1]]))

            #SOLVES NOT NOT
            self.not_not()
            
            #ASOCIATIVE PROPERTY
            self.asociate()

            #REDUCES EACH < TO A >
            if self.type == '<':
                self.type = '>'
                self[0], self[1] = self[1], self[0]

            #simplify 0's and 1's
            self.check_neutral_and_dominant()


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
    #Copy Builder   -> independent copy, (root=self)
    def copy__init__(self, other: 'LogicExpression'):
        if self is self.root:
            self.copy(other, 'i')
        else:
            self.copy(other, 'd')

    #copys other objet to self
    #mode= 'r' (reference)-> self = reference(other)
    #mode='i' (independent)-> new LogicExpression from other
    #mode='d' (deep)-> deepcopy   (default)
    def copy(self, other, mode:int='d'):
        if mode not in ('d', 'r', 'i'): return None

        self.type = other.type

        self.vars = other.vars.copy() if mode != 'r' else other.vars

        self.notation = other.notation.copy() if mode != 'r' else other.notation

        if mode == 'i':
            self.root = self
        elif mode== 'd':
            self.root = deepcopy(other.root)
        else:
            self.root = other.root

        self.__argument = deepcopy(other.__argument) if mode != 'r' else other.__argument

    ##########################################################################
    ##########################################################################

    def find_vars(self, leafs=[]):
        self.vars = dict({})
        leafs = self.get_leafs() if len(leafs) == 0 else leafs

        for leaf in leafs:
            if leaf[0].isalpha() and leaf[0] not in self.vars:
                self.vars[leaf[0]] = leaf[0]

    def get_leafs(self)->list['LogicExpression']:
        leafs = []

        if self.type == '!': self = self.__argument #changes self reference (local)

        if self.type == 'p':
            leafs.append(self)

        elif self.type in binary_connectors:
            for i in self.__argument:
                leafs += i.get_leafs()

        return leafs

    def get_super_leafs(self, super_leafs:list=[])->list['LogicExpression']:
        leafs = self.get_leafs()
        
        super_leafs = []

        i=0
        while i < len(leafs):
            super_leafs.append(leafs[i].root)
            i += len(leafs[i].root)
        
        return super_leafs

    def change_vars(self, changes:dict):
        if len(changes) < len(self.vars) : return None

        leafs = self.get_leafs()
        self.find_vars(leafs)

        new_vars = dict({})

        #creates the dictionary whith old_var_name:new_var_name
        if type(changes) == dict:
            self.vars.update(changes)
            new_vars = self.vars.copy()

        

        elif type(changes) in (list, tuple) and len(changes) >= len(self.vars):
            #Add each new_var whith the new name as value
            j=0
            for i in self.vars.keys():
                new_vars[i] = changes[j]
                j+=1
            
            #Add extra vars whith the same value as key
            while len (changes) > len(new_vars):
                new_vars[changes[j]] = changes[j]
                j += 1
    
        #changes the vars from the leafs
        for leaf in leafs:
            leaf.__argument = new_vars[leaf.__argument]

        self.vars = dict({})
        for value in new_vars.values():
            self.vars[value] = value

    def add_var(self, amount=1):
        i = 0
        while i < amount:
            var = random.choice(variables)
            if var not in self.vars:
                self.vars[var] = var
                i+=1

    def unify(self, other, modifying=False) -> tuple:
        #takes the smallest le
        little = self if len(self.vars) < len(other.vars) else other
        big = other if little is self else self

        #creates a new le adding necessary vars to compare
        new = LogicExpression(little)
        new.change_vars(big.vars)

        if modifying:   little.copy(new)

        #changes the necesary references
        if little is self: self = new
        else: other = new

        if not modifying: return (self, other)
        
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
        if self.type == '!':
            return LogicExpression(self.__argument)
        return LogicExpression(['!', self])
    def __invert__(self) ->'LogicExpression': return - self

    #Relational operators
    def __eq__ (self, other)->bool:
        return len(self.vars) == len(other.vars) and self.minterms() == other.minterms() 
    def __ne__ (self, other)->bool:
        return not self == other

    def __le__ (self, other)->bool:
        return self in other or other == self
    def __ge__ (self, other)->bool:
        return other in self or other == self
    def __lt__ (self, other)->bool:
        return self in other
    def __gt__ (self, other)->bool:
        return other in self

    def __contains__(self, other)->bool:
        if len(self.vars) - len(other.vars) != 0:
            self, other = self.unify(other)
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
        #for slicing
        if type(index) == int and index < 0:
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
                    self[term_index+1].root = self  #updates root
                    i-=1
                del self[term_index]
                term_index += lenght
        
            else: term_index += 1


    def not_not(self):
        if self.type == '!' and self.__argument.type == '!':
            self.copy(LogicExpression(self[0][0], self.root), 'r')


    def de_morgan(self, full=False):

        if self.type == '!' and self.__argument.type in ('&','|'):
            self.__argument.de_morgan()
            self.not_not()

        elif self.type in ('|', '&'):

            #Not for each component
            for i in range(len(self.__argument)):
                self[i] = - LogicExpression(self[i], self)

            self.type = '|' if self.type == '&' else '&'

            self.copy(- LogicExpression(self, self.root), 'r')

        #changes the refference (local change)
        if self.type == '!': self = self.__argument

        if self.type in ('&','|') and full :
            
            for i in range(len(self)):
                if self[i].type=='!':  self[i].de_morgan(True)


    def absorb(self):
        #deletes all equals
        if self.type == '|':
            i=0
            while i < len(self):

                j=0
                while j < len(self):
                    if j != i:
                        if self[i] <= self[j]: 
                            del self[i]
                            j = len(self)
                        else: j+=1
                    else: j+=1
                i+=1

        elif self.type == '&':
            i=0
            while i < len(self):

                j=0
                while j < len(self):
                    if j != i:
                        if self[i] >= self[j]: 
                            del self[i]
                            j = len(self)
                        else: j+=1
                    else: j+=1
                i+=1


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

        '''
        #TURNS CONNECTIVES IN ITS INITIAL NOTATION
        if self is self.root and type(self.__argument) not in (str, bool, int):
            string = list(string)

            for i in range(len(string)):

                if string[i] in self.notation.keys():
                    string[i] = self.notation[string[i]]

            string = string[1:-1]   #DELETE PARENTHESES (...)

            string = "".join(string)
        '''
        return string
    ##########################################################################


