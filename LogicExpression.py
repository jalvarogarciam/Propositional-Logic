from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors, variables, notation_out


from copy import deepcopy
import random

#from LogicSet import LogicSet as ls
class LogicExpression:
    '''
    The shape of LogicExpression's are like a "tree of expression". But, the main
    type is a Unary or Binary Connective. 

    ex:CONNECTIVE(CONNECTIVE(CONNECTIVE(...),CONNECTIVE(...))) on his leafs, we can
    found bool vars x,y,z...

    And then, it will be able to evaluate the expression with a __call__.
    '''
    ##########################################################################
    def __init__(self, arg:str = 0, root:"LogicExpression" = None, order:tuple=None):

        self.root = root if type(root) != type(None) else self


        self.__argument : LogicExpression|str|bool|int = []
        self.vars: list = []
        self.type: str


        if type(arg) == str: 

            if len(arg) > 1 : self.expr__init__(arg)
            elif arg.isdigit() : self.bool__init__(int(arg))
            else: self.proposition__init__(arg)


        elif type(arg) in (bool,int): self.bool__init__(arg)

        elif type(arg) in (tuple,list) : self.connective__init__(arg)

        elif type(arg) == LogicExpression : self.copy__init__(arg)

        if self.type not in ('p', '1', '0'): self.take_vars()

        if order != None: self.order(*order)

    ##########################################################################
    #Proposition builder
    def proposition__init__(self, proposition:str|list|tuple):
        self.type = 'p'
        self[0] = str(proposition)    #always is a char
        self.vars = [proposition]

    ##########################################################################
    #Bool builder
    def bool__init__(self, truth:bool|int):
        self.type = '1' if bool(truth) else '0'
        self[0] = bool(truth)

    ##########################################################################
    #Expression builder
    def expr__init__(self, raw_expression:str|list|tuple):

        if self.root is self:
        #if it´s a root and it´s not on polish notation
            i=0
            while raw_expression[i] in unary_connectors:    i+=1

            if raw_expression[i] not in binary_connectors: 
                raw_expression = usual_to_polish(raw_expression)

        self.type = raw_expression[0]


        #BUILDS A NEW L.E. FOR ARGUMENT.......................................

        #UNARY CONNECTIVES (!)
        if self.type in unary_connectors:

            self[0] = LogicExpression(raw_expression[1:], self)

        #BINARY CONNECTIVES +,*,<,>,=)
        else:   # self.type in binary_connectors:

            #LOCATES the range of the main connective
            #It's the same algorithm that we use to check if a polish expr is correct
            in_range,i = 1,1
            while in_range != 0 :
                if raw_expression[i] in binary_connectors: in_range+=1

                elif raw_expression[i] not in unary_connectors: in_range-=1

                i+=1

            #ARGUMENT BUILDING
            self[0] = LogicExpression(raw_expression[1:i], self)
            self[1] = LogicExpression(raw_expression[i:], self)

            if self.type in ('↚', '↛', '⊕', '↑', '↓'): self.strange_types()

        self.properties()

    ##########################################################################
    #connective Builder (list)
    def connective__init__(self,le_list:list|tuple):
        self.type = le_list[0]

        if self.type in unary_connectors: 
            self[0] = LogicExpression(le_list[1], root=self)
        
        else: #self.type in binary_connectors:
            for le in le_list[1:]:   self.append(LogicExpression(le, self))


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
    def copy(self, other, mode:str='d')->'LogicExpression':
        if mode not in ('d', 'r', 'i'):
            raise ValueError(f"mode {mode} no recognised. Did you mean ('d', 'r', 'i') ?")

        self.type = other.type

        self.vars = other.vars.copy() if mode != 'r' else other.vars

        if mode == 'i':
            self.root = self
        elif mode== 'd':
            self.root = deepcopy(other.root)
        else:
            self.root = other.root

        self.__argument = deepcopy(other.__argument) if mode != 'r' else other.__argument

        return self

    ##########################################################################
    ##########################################################################
    def take_vars(self):
        for i in range(len(self)):
            for i in self[i].vars:
                if i not in self.vars: self.vars += [i]

    def find_vars(self, leafs=[]):
        self.vars = []

        leafs = self.get_leafs() if len(leafs) == 0 else leafs

        for leaf in leafs:
            if leaf.type == 'p' and leaf.__argument not in self.vars:
                self.vars += leaf.__argument

    def get_leafs(self)->list['LogicExpression']:
        leafs = []

        if self.type == '!': self = self[0] #changes self reference (local)

        if self.type in ('p', '0', '1'):
            leafs.append(self)

        elif self.type in binary_connectors:
            for i in self:
                leafs += i.get_leafs()

        return leafs


    def get_super_leafs(self, leafs:list=[])->list['LogicExpression']:
        leafs = self.get_leafs() if len(leafs) == 0 else leafs

        super_leafs = []

        for l in leafs:
            if not l.root in super_leafs and not l.root is self:   
                super_leafs += [l.root]

        return super_leafs

    def get_all_leafs(self):
        all_leafs = super_leafs = self.get_leafs()
        first_leafs_len = len(all_leafs) #to know the max depth of deapest leafs
        
        while not all(elem in all_leafs for elem in self):
            super_leafs = self.get_super_leafs(super_leafs)
            for l in super_leafs: all_leafs += [l] if l not in all_leafs else []

        #sorted by levels of depth
        levels = [] #creates the new matrix
        for i in range(max(*(l.depth() for l in all_leafs[:first_leafs_len]))): 
            levels.append([])

        for l in all_leafs: #fills it
            levels[l.depth()-1].append(l)

        return levels

    #if changes is a dictionary, it will change (or add) the specified vars
    #if changes is a tuple or list, it will be the new vars
    #PRE: vars have been taken
    def change_vars(self, changes:dict):
        if type(changes) in (list, tuple) and len(changes) < len(self.vars): return None

        leafs = self.get_leafs()

        new_vars = {i:i for i in self.vars}

        #creates the dictionary whith old_var_name:new_var_name
        if type(changes) == dict:
            new_vars.update(changes)

        elif type(changes) in (list, tuple) and len(changes) >= len(self.vars):
            #Add each new_var whith new items
            j=0
            for key in new_vars:
                new_vars[key] = changes[j]
                j+=1

        #changes the vars from the leafs
        for leaf in leafs:
            if leaf.type == 'p': leaf.__argument = new_vars[leaf.__argument]

        #updates self vars
        if type(changes) in (tuple, list): self.vars = {value for value in changes}
        elif type(changes) == dict : self.vars = [value for value in changes.values()]


    # adds {amount} random vars, default 1
    def add_var(self, amount=1):
        i = 0
        while i < amount:
            var = random.choice(variables)
            if var not in self.vars:
                self.vars += [var]
                i+=1

    # unifies the vars (order, names, and amount).
    def unify(self, other, modifying=False) -> tuple:
        if self.vars == other.vars : 
            return self, other #if they have the same vars and vars have the same order

        #takes the smallest le
        little = self if len(self.vars) < len(other.vars) else other
        big = other if little is self else self

        #creates a new le adding necessary vars to compare
        new = LogicExpression(little)
        new.change_vars(big.vars)

        #changes the necesary references
        if little is self: self = new
        else: other = new

        if modifying:   little.copy(new)
        return ([self, other])
    
    def order(self, *order)->tuple:
        if len(order) != 0: self.vars = [i for i in order]
        return tuple(self.vars)



    ###########################################################################
    #OPERATORS
    ###########################################################################
    #Arithmetic operators
    def __add__(self, other) ->'LogicExpression':
        #self, other = self.unify(other)
        return LogicExpression(['+', self, other])
    def __or__(self, other) ->'LogicExpression': return self + other
    
    def __mul__(self, other) ->'LogicExpression':
        #self, other = self.unify(other)
        return LogicExpression(['*', self, other])
    def __and__(self, other) ->'LogicExpression': return self * other

    def __xor__(self, other) ->'LogicExpression':
        return (-self * (other)) + (self * (-other))

    def __sub__(self, other) ->'LogicExpression': return self * -(self*other)

    def __neg__(self) ->'LogicExpression':
        if self.type == '!':
            return LogicExpression(self[0])
        return LogicExpression(['!', self])
    def __invert__(self) ->'LogicExpression': return - self

    #Relational operators
    def __eq__ (self, other)->bool:
        return hash(self) == hash(other)
        if set(self.vars) != set(other.vars): return False

        self, other = self.unify(other)
        return self.minterms() == other.minterms()

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
        self, other = self.unify(other)
        return self.minterms().issuperset(other.minterms())


    def __hash__(self) -> int:
        string = str(self)

        while not self is self.root:
            string = str(self.root) + string
            self = self.root
        
        return hash(string)

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
    
    #depth is defined as the number of steps between the main root and the leaf 
    # provided (self)
    def depth(self)->int:
        depth=0
        while not self is self.root:
            depth+=1
            self = self.root
        return depth
            

    ########Items
    def __getitem__(self,index:int)->'LogicExpression': 

        if type(index) == int and index < 0:
            the_root = self.root
            i = -1
            while i > index and the_root != the_root.root: 
                the_root = the_root.root
                i-=1
            return the_root

        #for slicing
        else:
            if self.type in ('p', '0', '1') : return self.__argument
            elif self.type == '!': return self.__argument
            else : return self.__argument[index]

    def __setitem__(self, index, value):
        if self.type in ('p', '0', '1'): self.__argument = value
        else:
            if type(value) != LogicExpression: value = LogicExpression(value)

            if self.type == '!':    self.__argument = value
            else:
                if len(self.__argument) > index:
                    self.__argument[index] = value
                else:
                    self.__argument.append(value)

    def __delitem__(self,index):
        if self.type in ('p', '0', '1', '!'): del self.__argument
        else : del self.__argument[index]
    
    def __iter__(self):
        if self.type in ('p', '0', '1', '!'):
            return iter(list([self.__argument]))
        else:
            return iter(self.__argument)

    def append(self, *args):
        if type(self.__argument) != list: return None
        for arg in args: self.insert(len(self.__argument), arg)

    def insert(self, index: int, *args):
        if type(self.__argument) != list: return None
        for arg in args:
            if type(arg) != LogicExpression: arg = LogicExpression(arg)
            self.__argument.insert(index, arg)
    ##########################################################################
    ###########################################################################




    #Main propperties##########################################################
    def properties(self):
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

    def strange_types(self):

        if self.type == '⊕': self.type = '='
        elif self.type == '↛': self.type = '>'
        elif self.type == '↑': self.type = '*'
        elif self.type == '↓': self.type = '+'
        elif self.type == '↚':
            self.type = '<'
            self[0], self[1] = self[1], self[0]

        self.copy(-self,'r')


    def check_neutral_and_dominant(self):
        if self.type not in ('>', '*', '+'): return None
        i=0
        while i < (len(self)):

            if self[i].type == ('0'):

                if self.type == '+': 
                    del self[i]
                    if len(self) == 1:
                        if not (self.root is self):
                            self[0] = self.root
                        self.copy(self[0])

                elif self.type == '*':
                    self.copy(LogicExpression(0))
                
                elif self.type == '>' and i==0:
                    self.copy(LogicExpression(1))

            elif self[i].type == ('1'):

                if self.type == '*': 
                    del self[i]
                    if len(self) == 1: 
                        if not (self.root is self):
                            self[0] = self.root
                        self.copy(self[0])

                elif self.type == '+':
                    self.copy(LogicExpression(1))
            i+=1

    def asociate(self):
        if self.type not in ('+','*'): return None

        term_index = 0

        for x in range(len(self)):

            if self[term_index].type == self.type:

                lenght = len(self[term_index])

                i = lenght - 1
                while i >= 0:
                    self.insert(term_index+1, self[term_index][i])
                    self[term_index+1].root = self  #updates root
                    i-=1
                del self[term_index]
                term_index += lenght
        
            else: term_index += 1

    def distribute(self): ...

    def not_not(self):
        if self.type == '!' and self[0].type == '!':
            self[0] = self[0][0]
            self[0].root = self


    def de_morgan(self, full=False):

        if self.type == '!' and self[0].type in ('*','+'):
            self[0].de_morgan()
            self.not_not()

        elif self.type in ('+', '*'):

            #Not for each component
            for i in range(len(self)):
                self[i] = - LogicExpression(self[i], self)

            self.type = '+' if self.type == '*' else '*'

            self.copy(- LogicExpression(self, self.root), 'r')

        #changes the refference (local change)
        if self.type == '!': self = self[0]

        if self.type in ('*','+') and full :
            
            for i in range(len(self)):
                if self[i].type=='!':  self[i].de_morgan(True)


    def absorb(self):
        #deletes all equals
        if self.type == '+':
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

        elif self.type == '*':
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
    def __call__(self,*args)->bool:
        truth : bool = False

        if len(args) == 0: return self.truth_board()

        elif len(args) > 1: 
            vars = {}
            for value,var in zip(args,self.vars):
                vars.update({var:int(value)})

        else: vars = args[0]
        #Basics
        if self.type == 'p': truth = bool(vars[self[0]])

        elif self.type in ('0','1'): truth = bool(self[0])

        #Recursivity
        elif self.type == '!': truth = not bool(self[0](vars))

        elif self.type in binary_connectors:

            truth_list:list = []

            #TURNS each argument INTO A BOOL VALUE
            #operator __call__ -> evaluate
            for e in self:  truth_list += [e(vars)]

            if self.type == '*':
                truth = True
                for i in range(len(truth_list)): truth &= truth_list[i]

            elif self.type == '+':
                truth = False
                for i in range(len(truth_list)): truth |= truth_list[i]

            elif self.type == '>':
                truth = (not truth_list[0]) or truth_list[1]
            elif self.type == '<':
                truth = (not truth_list[1]) or truth_list[0]
            elif self.type == '=':
                truth = ((truth_list[0]) and truth_list[1]) or \
                        ((not truth_list[1]) and not truth_list[0])

            elif self.type == '⊕':
                truth = ((not truth_list[0]) and truth_list[1]) or \
                        ((not truth_list[1]) and truth_list[0])

            elif self.type == '↚':
                truth = not (truth_list[0] or (not truth_list[1]))

            elif self.type == '↛':
                truth = not ((not truth_list[0]) or truth_list[1])

            elif self.type == '↑':
                truth = not (truth_list[0] and truth_list[1])

            elif self.type == '↓':
                truth = not (truth_list[0] or truth_list[1])

        return (1 if truth else 0)


    def truth_board(self)->tuple:

        if len(self.vars) == 0: self.find_vars()

        board = []

        values = dict({})
        for v in self.vars: values.update({v:0})

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

        return (tuple(self.vars), board)

    ###########################################################################

    def to_canonical_shape(self,on_minterms=True)->'LogicExpression':
        if self.type.isdigit(): return LogicExpression(self)    #for 1, 0

        if len(self.vars) == 0: self.find_vars()


        num_vars = len(self.vars)

        minterms = tuple(self.minterms())
        maxterms = tuple(set(range(2**num_vars)) - set(minterms))

        terms = minterms if on_minterms else maxterms

        symbol = '*' if on_minterms else '+'

        le_list = []
        for i in terms:
            binary = dec_binbol(i,num_vars)

            string = ""
            i=0
            if on_minterms:
                for bit in binary:
                    oposite = '!' if not bit else ''
                    string += oposite + self.vars[i] + symbol
                    i += 1
            else:
                for bit in binary:
                    oposite = '!' if bit else ''
                    string += oposite + self.vars[i] + symbol
                    i += 1

            string = '('+string[:-1]+')'

            le_list.append(LogicExpression(string))

        symbol = '*' if symbol=='+' else '+'
        le_list.insert(0,symbol)

        copy = LogicExpression(le_list) if len(le_list) > 1 else LogicExpression(str(self))

        return copy


    # Minterms / Maxterms######################################################
    def to_boolean_logic(self):

        leafs = self.get_all_leafs()

        for level in leafs:

            for l in level:

                if l.type == '=':
                    l.type = '*'
                    l[0], l[1] = (-l[0] + l[1]), (-l[0] + l[1])

                elif l.type == '>':
                    l.type = '+'
                    l[0] = -l[0]


    def minterms(self)->set: return self.canonical_terms(True)
    def maxterms(self)->set: return self.canonical_terms(False)
    def canonical_terms(self,on_minterms=True):

        if len(self.vars) == 0: self.find_vars()

        terms = []

        values = dict({})
        for v in self.vars: values.update({v:0})

        num_vars = len(self.vars)

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
    
    def to_clauses(self):

        self = self.copy()

        self.to_boolean_logic()

        lset = ls()


        return lset


    ###########################################################################



    #CASTING##################################################################

    def __bool__(self)->bool:
        return self.istautology()


    def __str__(self)->str:

        string = ""

        if self.type in binary_connectors:
        
            for i in range(len(self)):

                string += str(self[i]) + ' ' + self.type + ' '

            string = string[:-3] # removes the last connective

        if self.type in unary_connectors:

            if self[0].type == 'p':
                string += self.type + str(self[0])

            elif self[0].type in ('0','1'): 
                string+= str(int(not bool(self[0][0])))

            else:
                string += self.type + str(self[0])
        
        elif self.type in ('p','0','1'):
            string += self[0] if self.type == 'p' else str(int(self[0]))


        string = list(string)
        for i in range(len(string)):
            if string[i] in notation_out: string[i] = notation_out[string[i]]
        string = "".join(string)

        if not self.root is self:
            if self.type in binary_connectors or \
            self.type == '!' and self[0].type in binary_connectors:
                string = '(' + string + ')'


        return string
    ##########################################################################

















from LogicExpression import LogicExpression as le
class ls:
    def __init__(self, *args):

        self.__clauses : list = []

        if len(args) == 0: ...

        elif type(args[0]) == ls:
            self.__clauses = args[0].__clauses.copy()

        elif type(args[0]) != le and len(args) == 1: self.__clauses = list(args[0])

        else : self.__clauses = list(args)

    # [] item access
    def __getitem__(self,index:int)->'LogicExpression': return self.__clauses[index]
    def __setitem__(self, index, value): self.__clauses[index] = LogicExpression(value)
    def __delitem__(self,index): del self.__clauses[index]


    def __len__(self)->int:
        return len(self.__clauses)

    def __add__(self, other) ->'ls': 
        result = ls(self)
        #clauses can't be repeated
        for c in other.__clauses:
            if c not in result.__clauses: result.__clauses += [c]
        return result
    def __or__(self, other) ->'ls': return self + other
    def __mul__(self, other) ->'ls': return self + other
    def __and__(self, other) ->'ls': return self * other

    def __sub__(self, other) ->'ls':
        clauses_difference = self.__clauses.copy()
        clauses_difference.remove(*(~other))


    #returns a copy of the clauses' list
    def __invert__(self):
        return ls(self).__clauses


    #Relational operators
    def __eq__ (self, other)->bool:
        return self.__clauses == other.__clauses
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
        return set(self.__clauses).issuperset(set(other.__clauses))


    def __str__(self):
        if len(self) == 0: return ""
        string = str(self.__clauses[0]) 
        for exp in self.__clauses[1:]:
            string += ', ' + str(exp)

        return string
