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
    '''
    Builds a new Logic Expression with the args provided.
        -if ltype is specified, args will be understood as a list of LogicExpressions
        -if order is specified, it will be the vars' list
        -if root is provided, it will be the instance's root
            PRE:self must be a part of it's argument
    '''
    def __init__(self, *args, ltype='', root:"LogicExpression" = None, order:tuple=None):
        if len(args) == 0: args = [0]   #default arg

        self.__root = root if type(root) != type(None) else self
        self.__argument : LogicExpression|str|bool|int = []
        self.__vars: list = []
        self.__type: str = ltype


        if ltype != '': self.connective__init__(args)
        else:
            if type(args[0]) == str: 
                if len(args[0]) > 1 : self.expr__init__(args[0])
                elif args[0].isdigit() : self.bool__init__(int(args[0]))
                else: self.proposition__init__(args[0])
            elif type(args[0]) in (bool,int): self.bool__init__(args[0])
            elif type(args[0]) == LogicExpression : self.copy__init__(args[0])


        if self.type in connectors: self.take_vars()

        if order != None: self.order(*order)

    ##########################################################################
    #Proposition builder
    def proposition__init__(self, proposition:str|list|tuple):
        self.__type = 'p'
        self[0] = str(proposition)    #always is a char
        self.__vars = [proposition]

    ##########################################################################
    #Bool builder
    def bool__init__(self, truth:bool|int):
        self.__type = '1' if bool(truth) else '0'
        self[0] = bool(truth)

    ##########################################################################
    #Expression builder
    def expr__init__(self, raw_expression:str|list|tuple):

        #ON POLISH NOTATION???
        if self.isroot():
        #if it´s a root and it´s not on polish notation
            i=0
            while raw_expression[i] in unary_connectors:    i+=1
            #checks if it's on polish notation
            if raw_expression[i] not in binary_connectors: 
                raw_expression = usual_to_polish(raw_expression)

        self.__type = raw_expression[0]


        #ARGUMENT'S CONSTRUCTION

        ##for unary connectives (!)
        if self.type in unary_connectors:

            self[0] = LogicExpression(raw_expression[1:], self)

        #for binnary connectives +,*,<,>,=)
        else:   # self.type in binary_connectors:

            #LOCATES the range of the main connective
            #It's the same algorithm that we use to check if a polish expr is correct
            in_range,i = 1,1
            while in_range != 0 :
                if raw_expression[i] in binary_connectors: in_range+=1

                elif raw_expression[i] not in unary_connectors: in_range-=1

                i+=1

            #It is divided into two parts
            self.append(
                LogicExpression(raw_expression[1:i], root=self),
                LogicExpression(raw_expression[i:], root=self)
            )

            if self.type in ('↚', '↛', '⊕', '↑', '↓'): self.strange_types()

        self.properties()

    ##########################################################################
    #connective Builder (list)
    def connective__init__(self,le_list:list|tuple):
        for le in le_list:  self.append(LogicExpression(le.copy(), root=self))

    ##########################################################################
    #Copy Builder   -> by refference
    def copy__init__(self, other: 'LogicExpression'):
        self.__argument = other.__argument
        self.__vars = other.__vars
        if self.isroot() and not other.isroot(): self.__root = other.__root
        self.__type = other.__type

    '''copys other objet to self deeply or returns a deepcopy of self if 
    'other' is not given.
        if mode='i' (independent)-> like deep but without copying roots
        if mode='d' (deep)-> deepcopy   (by default)'''
    def copy(self, other:'LogicExpression'=None, mode:str='d')->'LogicExpression':
        if mode not in ('d', 'i'):
            raise ValueError(f"mode {mode} not recognised. Did you mean ('d','i') ?")

        if type(other) == LogicExpression:   #modifying self if other != None
            self.__type = other.type
            self.__vars = other.vars
            self.__argument = deepcopy(other.__argument)
            self.__root = self if mode == 'i' or other.isroot() else deepcopy(other.__root) 
            return self
        else: return le().copy(self,mode)



    ########Items
    @property
    def type(self)->str:    return self.__type
    @type.setter
    def type(self, value:str): self.change_type(value)
    @property
    def vars(self)->str:    return self.__vars.copy()
    @vars.setter
    def vars(self, changes): self.change_vars(changes)

    def __len__(self)->int:
        if type(self.__argument)==list: return len(self.__argument) #for (+,*,=,>)
        else: return 1  #for (!,p,0,1)

    def __getitem__(self,index:int)->'LogicExpression': 
        #for Roots
        if type(index) == int and index < 0:  #index's type checking is for slicing
            the_root = self.__root
            i = -1
            while i > index and the_root != the_root.__root: 
                the_root = the_root.__root
                i-=1
            return the_root
        #for Arguments
        else:
            if self.type in ('p', '0', '1') : return self.__argument
            elif self.type == '!': return self.__argument
            else : return self.__argument[index]

    def __setitem__(self, index, value):
        if index < 0: raise IndexError('IndexError: root assignation is not allowed')

        if self.type in ('p', '0', '1', '!'): 
            if self.type == '!':
                self.__argument = LogicExpression(value, root=self)
            else:   self.__argument = value

        else: self.__argument[index] = LogicExpression(value, root=self)
        self.take_vars()#updating the vars

    def __delitem__(self,index):
        if self.type in ('p', '0', '1', '!'): del self.__argument
        else :  del self.__argument[index]

    def __iter__(self):
        if self.type in ('p', '0', '1', '!'):
            return iter([self]) if self.type != '!' else iter(self[0])
        else:
            return iter(self.__argument)

    def append(self, *args):
        if self.type in binary_connectors:
            for arg in args: self.insert(len(self.__argument), arg)
        else:   self.__argument = args[0]

    def insert(self, index: int, *args):
        if type(self.__argument) != list: return None
        for arg in args:
            if type(arg) != LogicExpression: arg = LogicExpression(arg)
            self.__argument.insert(index, arg)
    ##########################################################################
    ##########################################################################
    def take_vars(self):
        for l in self:
            for var in l.__vars: self.__vars += var if var not in self.__vars else []

    def find_vars(self, leafs=[]):
        self.__vars = []

        leafs = self.get_leafs() if len(leafs) == 0 else leafs

        for leaf in leafs:
            if leaf.type == 'p' and leaf[0] not in self.__vars:
                self.__vars += leaf[0]

    def get_leafs(self)->list['LogicExpression']:
        leafs = []

        if self.type == '!': leafs += self[0].get_leafs() #changes self reference (local)

        if self.type in ('p', '0', '1'):    leafs.append(self)

        elif self.type in binary_connectors:
            for l in self:  leafs += l.get_leafs()

        return leafs


    def get_super_leafs(self, leafs:list=[])->list['LogicExpression']:
        leafs = self.get_leafs() if len(leafs) == 0 else leafs
        super_leafs = ls([])

        for l in leafs:
            if not l.isroot():
                super_leafs += l.root

        return super_leafs

    def get_all_leafs(self):
        all_leafs = super_leafs = ls(self.get_leafs())
        max_depth = max(*(l.depth() for l in all_leafs)) #to know the max level of the matrix

        while not all(elem in all_leafs for elem in self):
            super_leafs = self.get_super_leafs(super_leafs)
            for l in super_leafs:   all_leafs += l

        #sorted by levels of depth
        levels = [*([] for i in range(max_depth))] #creates the new matrix

        for l in all_leafs: #fills it
            levels[l.depth()-1].append(l)

        return levels

    def change_type(self, value):
        if self.type in ('!','0','1','p') or value in ('!','0','1','p'): 
            raise AttributeError("!, p, 0, 1 types can't change")
        elif value not in ('>', '=', '+', '*'):
            raise AttributeError(f"{value} is a non supported type")
        if value in ('>', '=') and len(self) > 2:
            raise AttributeError("implication and biconditional "+ \
                                 f"always  have 2 arguments, it has {len(self)}")
        self.__type = value

    '''if changes is a dictionary, it will change (or add) the specified vars
       if changes is a tuple or list, it will be the new vars
    #PRE: vars have been taken'''
    def change_vars(self, changes:dict):
        if type(changes) in (list, tuple) and len(changes) < len(self.__vars): return None

        leafs = self.get_leafs()

        new_vars = {i:i for i in self.__vars}

        #creates the dictionary whith old_var_name:new_var_name
        if type(changes) == dict:
            self.__vars = list(changes.values())
            new_vars.update(changes)

        elif type(changes) in (list, tuple):
            changes = list(changes)
            self.__vars = changes.copy()
            #Add each new_var whith new items
            j=0
            for key in new_vars:
                if key in self.__vars:    changes.remove(key)
                else:
                    new_vars[key] = changes[j]
                    j+=1

        #changes the vars from the leafs
        for leaf in leafs:
            if leaf.type == 'p': leaf[0] = new_vars[leaf[0]]



    # adds {amount} random vars, default 1
    def add_var(self, amount=1):
        i = 0
        while i < amount:
            var = random.choice(variables)
            if var not in self.__vars:
                self.__vars += [var]
                i+=1

    # returns two LE with the same vars' list
    def unify(self, other:'LogicExpression', modifying=False) -> tuple:
        if self.__vars == other.__vars : return self, other 
        #if they have the same vars with the same order

        #creates a new le adding necessary vars to compare
        new_self, new_other = LogicExpression(self), LogicExpression(other)
        new_other.__vars  = new_self.__vars = list(set(self.__vars + other.__vars)) #there isn't repeated vars

        if modifying:   self.__vars, other.__vars = new_self.__vars, new_other.__vars

        return ([new_self, new_other])

    def order(self, *order)->tuple:
        if len(order) != 0: self.__vars = list(order)
        return tuple(self.__vars)


    ###########################################################################
    #OPERATORS
    ###########################################################################
    #Arithmetic operators
    def __add__(self, other) ->'LogicExpression':
        return LogicExpression(self, other, ltype='+')
    def __or__(self, other) ->'LogicExpression': return self + other

    def __mul__(self, other) ->'LogicExpression':
        return LogicExpression(self, other, ltype='*')
    def __and__(self, other) ->'LogicExpression': return self * other

    def __xor__(self, other) ->'LogicExpression':
        return (-self * (other)) + (self * (-other))

    def __sub__(self, other) ->'LogicExpression': return self * -(self*other)

    def __neg__(self) ->'LogicExpression':
        print("hola")
        return LogicExpression(self, ltype='!')
    def __invert__(self) ->'LogicExpression': return - self

    #Relational operators
    def __eq__ (self, other:'LogicExpression')->bool:
        if self.type in ('p', '0', '1', '!') and self.type == other.type:
            return self[0] == other[0]

        self, other = self.unify(other)

        return self.minterms() == other.minterms()

    def __ne__ (self, other)->bool:
        return not self == other

    def __contains__(self, other)->bool:
        return self >= other

    def __hash__(self) -> int:
        string = str(self)

        while not self.isroot():
            string = str(self.__root) + string
            self = self.__root

        return hash(string)



    def __le__ (self, other)->bool:# self <= other
        self, other = self.unify(other)
        return self.minterms() <= other.minterms()
    def __ge__ (self, other)->bool:# self >= other
        self, other = self.unify(other)
        return self.minterms() >= other.minterms()
    def __lt__ (self, other)->bool:# self < other
        self, other = self.unify(other)
        return self.minterms() < other.minterms()
    def __gt__ (self, other)->bool:# self > other
        self, other = self.unify(other)
        return self.minterms() > other.minterms()


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


    
    #depth is defined as the number of steps between the main root and the leaf 
    # provided (self)
    def depth(self)->int:
        depth=0
        while not self.isroot():
            depth+=1
            self = self.__root
        return depth
    

    def isroot(self)->bool: return self is self.__root

    ###########################################################################




    #Main propperties##########################################################
    def properties(self):
        #SOLVES NOT NOT
        self.not_not()

        #ASOCIATIVE PROPERTY
        self.asociate()

        #REDUCES EACH < TO A >
        if self.type == '<':
            self.__type = '>'
            self[0], self[1] = self[1], self[0]

        #simplify 0's and 1's
        self.check_neutral_and_dominant()

    def strange_types(self):

        if self.type == '⊕': self.__type = '='
        elif self.type == '↛': self.__type = '>'
        elif self.type == '↑': self.__type = '*'
        elif self.type == '↓': self.__type = '+'
        elif self.type == '↚':
            self.__type = '<'
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
                        if not self.isroot():
                            self[0] = self.__root
                        self.copy(self[0])

                elif self.type == '*':
                    self.copy(LogicExpression(0))
                
                elif self.type == '>' and i==0:
                    self.copy(LogicExpression(1))

            elif self[i].type == ('1'):

                if self.type == '*': 
                    del self[i]
                    if len(self) == 1: 
                        if not self.isroot():
                            self[0] = self.__root
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
                    self[term_index+1].__root = self  #updates root
                    i-=1
                del self[term_index]
                term_index += lenght

            else: term_index += 1


    def distribute(self):
        if not all(l.type in ('+', '*') for l in self) or \
        self.type not in ('+', '*'):                        return None

        


    def not_not(self):
        if self.type == '!' and self[0].type == '!':
            self[0][0].__root = self.__root
            self.copy(self[0][0])


    def de_morgan(self, full=False):

        if self.type == '!' and self[0].type in ('*','+'):
            self[0].de_morgan()
            self.not_not()

        elif self.type in ('+', '*'):

            #Not for each component
            for i in range(len(self)):
                self[i] = - LogicExpression(self[i], self)

            self.__type = '+' if self.type == '*' else '*'

            self.copy(- LogicExpression(self, self.__root), 'r')

        #changes the refference (local change)
        if self.type == '!': self = self[0]

        if self.type in ('*','+') and full :
            
            for i in range(len(self)):
                if self[i].type=='!':  self[i].de_morgan(True)


    def absorb(self):
        if self.type not in ('+','*'): return None

        #deletes all equals
        i= len(self) - 1
        while i >= 1:
            j=i-1

            isolated = self[:i]  #self.__argument without i and those just tested
            while j >= 0 and not\
            ((isolated[j]>= self[i] and self.type == '+') or \
             (self[i] >= isolated[j] and self.type == '*')):
                j -= 1
            # if didn't arrive the start, the second condition wasn't true
            if j != -1: del self[i] 

            i-=1


    ###########################################################################



    #Truth values#############################################################
    def __call__(self,*args)->bool:
        truth : bool = False

        if len(args) == 0: return self.truth_board()

        elif len(args) > 1: 
            vars = {}
            for value,var in zip(args,self.__vars):
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

        if len(self.__vars) == 0: self.find_vars()

        board = []

        values = dict({})
        for v in self.__vars: values.update({v:0})

        num_vars = len(self.__vars)

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

        return (tuple(self.__vars), board)

    ###########################################################################

    def to_canonical_shape(self,on_minterms=True)->'LogicExpression':
        if self.type.isdigit(): return LogicExpression(self)    #for 1, 0

        if len(self.__vars) == 0: self.find_vars()


        num_vars = len(self.__vars)

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
                    string += oposite + self.__vars[i] + symbol
                    i += 1
            else:
                for bit in binary:
                    oposite = '!' if bit else ''
                    string += oposite + self.__vars[i] + symbol
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

        if len(self.__vars) == 0: self.find_vars()

        terms = []

        values = dict({})
        for v in self.__vars: values.update({v:0})

        num_vars = len(self.__vars)

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

        if not self.isroot() :
            if self.type in binary_connectors or \
            self.type == '!' and self[0].type in binary_connectors:
                string = '(' + string + ')'

        return string
    ##########################################################################

















from LogicExpression import LogicExpression as le
class ls(list):
    def __init__(self, *args):

        if all(type(elem) == le for elem in args):  super().__init__(list(args))

        elif type(args[0]) in (ls, list):
            super().__init__(args[0].copy())






    def __add__(self, other) ->'ls':
        result = ls(self)

        if type(other) == ls:
            #clauses can't be repeated
            for c in other:
                if ls(c) not in result: result.append(c)

        elif type(other) == le:
            if other not in self:  result.append(other)
        return result
    def  __iadd__(self, other) ->'ls': return self.copy(self+other)

    def __or__(self, other) ->'ls': return self + other
    def __mul__(self, other) ->'ls': return self + other
    def __and__(self, other) ->'ls': return self * other

    def __sub__(self, other) ->'ls':
        if type(other) != ls: other = ls(other)

        sub = ls()
        for c in self:
            if ls(c) not in other:  sub.append(c)
        return sub
    def  __isub__(self, other) ->'ls':  return self.copy(self-other)

    #Relational operators
    def __eq__ (self, other)->bool:
        return all(c in other for c in self) and len(other) == len(self)
    def __ne__ (self, other)->bool:
        return not self == other
    
    def __contains__ (self, other)->bool:
        if type(other) == le:
            for c in self:
                if hash(c) == hash(other): return True
            return False

        elif type(other) == ls:
            all_in = True
            for c in other: all_in &= c in list(self)
            return all_in

    def __le__ (self, other)->bool:
        return self in other or other == self
    def __ge__ (self, other)->bool:
        return other in self or other == self
    def __lt__ (self, other)->bool:
        return self in other
    def __gt__ (self, other)->bool:
        return other in self


    def __str__(self):
        if len(self) == 0: return ""

        string = str(self[0])[1:-1]
        for c in self[1:]:
            string += ', ' + str(c)[1:-1]

        return string

    def copy(self, other=[])->'ls':
        if other == []: return ls(*(LogicExpression(c,c.root) for c in self))
        else:
            self.clear()
            self.extend(other.copy())
            return self



