from conectors import usual_to_polish, unary_connectors, binary_connectors, connectors, DEBUG, \
dec_binbol, all_connectors, variables, notation_out


from copy import deepcopy
import random

#from LogicSet import LogicSet as ls    

class LogicExpression:
    '''
    The shape of LogicExpression's are like a "tree of expressions" where each one
    is connected with its leafs and its root. 
    The types allowed are Unary(!) or Binary Connective(+,*,>,=), a proposition(p), 
    or a bool(b). 
    '''
    ##########################################################################

    def __init__(self, *args, ltype='', root:"LogicExpression" = None, order:tuple=None):
        '''
    Builds a new Logic Expression with the args provided.
        -if ltype is specified, args will be understood as a list of LogicExpressions
        -if order is specified, it will be the vars' list
        -if root is provided, it will be the instance's root if self is a part of
        its argument.
    '''    
        if len(args) == 0: args = [0]   #default arg

        self.__root = self
        self.__args : list[LogicExpression]|str|bool = []
        self.__vars: list = []
        self.__type: str = ltype


        if ltype != '': self.__typed_init(args)
        else:
            if type(args[0]) == str: 
                if len(args[0]) > 1 : self.__expr_init(args[0])
                elif args[0].isdigit() : self.__bool_init(int(args[0]))
                else: self.__prop_init(args[0])
            elif type(args[0]) in (bool,int): self.__bool_init(args[0])
            elif type(args[0]) == LogicExpression : self.__copy_init(args[0])
        if root is not None:  self.root = root

        self.take_vars()

        if order is not None: self.order(*order)

    ##########################################################################
    #Proposition builder
    def __prop_init(self, proposition:str):
        self.__type = 'p'
        self.__args = str(proposition)    #always is a char

    ##########################################################################
    #Bool builder
    def __bool_init(self, truth:bool|int):
        self.__type = 'b'
        self.__args = bool(truth)

    ##########################################################################
    #Expression builder
    def __expr_init(self, raw_expression:str|list|tuple):

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
        if self.type in unary_connectors:   #for unary connectives (!)

            self.__args = [LogicExpression(raw_expression[1:])]
            self.__args[0].__root = self

        else:   #for binnary connectives +,*,<,>,=)

            #LOCATES the range of the main connective
            #It's the same algorithm that we use to check if a polish expr is correct
            in_range,i = 1,1
            while in_range != 0 :
                if raw_expression[i] in binary_connectors: in_range+=1
                elif raw_expression[i] not in unary_connectors: in_range-=1
                i+=1

            #It's divided into two parts
            self.__args = [
                LogicExpression(raw_expression[1:i]),
                LogicExpression(raw_expression[i:])
            ]
            self.__args[0].__root = self.__args[1].__root = self
            self.strange_types()

        self.properties()

    ##########################################################################
    #connective Builder (list)
    def __typed_init(self,args:tuple):
        self.append(*args)
        self.properties()

    ##########################################################################
    #Copy Builder   -> by refference
    def __copy_init(self, other: 'LogicExpression'): self.copy(other)
    def copy(self, other:'LogicExpression'=None, mode:str='d')->'LogicExpression':
        '''copys other objet to self deeply or returns a deepcopy of self if 
        'other' is not given.\n
            if mode='i' (independent)-> like deep but without copying roots.\n
            if mode='d' (deep)-> deepcopy   (by default).
        '''
        if mode not in ('d', 'i'):
            raise ValueError(f"mode {mode} not recognised. Did you mean ('d','i') ?")

        if other is not None:   #modifying self
            self.__type = other.type
            self.__vars = other.vars

            if mode == 'i' or other.isroot(): 
                other_real_root, other.__root = other.__root, None
                if self.type not in ('p','b'): #other.__root was temporaly changed to avoid copiying it.
                    for arg in other.__args: arg.__root = None #args root are temporaly changed to avoid copiying it
                    self.__args = deepcopy(other.__args)
                    for arg in self.__args: arg.__root = self #solve args refferences
                    for arg in other.__args: arg.__root = other #restore other's args' root refference
                else: self.__args = other.__args    #both are unvariale types
                self.__root , other.__root = self, other_real_root #restore other's root refference
            else:
                index = other.__root.index(other, False)
                self.__root = deepcopy(other.__root)
                if self.type not in ('p', 'b'): 
                    self.__args = self.__root.__args[index].__args #just copied
                    for arg in self.__args: arg.__root = self #solve args refferences
                else: self.__args =  other.__args
                self.__root.__args[index] = self    #solve root's refferences
            return self
        else: return le().copy(self,mode)

    def __hash__(self) -> int:
        '''It's based on the coordinates from the root to self and 
        the str representation of the main root'''
        if self.isroot():   components = ('R', str(self))
        else:
            indexes = []
            current = self
            while not current.isroot():
                indexes += [current.__root.index(current)]
                current = current.__root
            components = (tuple(indexes), str(current))
        return hash(components)

    #elevates a leaf to the supperior level: self = self[index] (adjusting roots)
    def up(self):
        old_root = None if self[-1].isroot() else self[-2]
        self[-1].copy(self,'i')
        self = self[-1]
        self.__root = old_root if old_root is not None else self



    ########Items
    @property
    def type(self)->str:    return self.__type
    @type.setter
    def type(self, value:str): self.change_type(value)
    @property
    def vars(self)->str:    return self.__vars.copy()
    @vars.setter
    def vars(self, changes): self.change_vars(changes)
    @property
    def root(self)->'LogicExpression':  return self.__root.copy()
    @root.setter
    def root(self, value:'LogicExpression'): self.change_root(value)


    def __len__(self)->int:
        if type(self.__args)==list: return len(self.__args) #for (+,*,=,>)
        else: return 1  #for (!,p,0,1)

    def __getitem__(self,index:int)->'LogicExpression': 
        #for roots
        if type(index) == int and index < 0:
            root = self
            for i in range(-index): root = root.__root
            return root
        #for args
        return self.__args[index] if self.type not in ('p', 'b') else self.__args

    def __setitem__(self, index, value):
        if type(index) == slice: raise TypeError('slicing is not allowed')
        if index < 0: raise IndexError('root assignation is not allowed')

        if self.type in ('p', 'b'): self.__args = value
        else: 
            self.__args[index] = value.copy(mode='i')
            self.__args[index].__root = self
        
        self.take_vars()#updating the vars
        self.properties()

    def __delitem__(self,index):
        if self.type in ('p', 'b'):
            raise Exception(f"single types component like '{self.type}' can't be deleted")
        elif self.type == '!':
            del self.__args[0][index]
        else :
            del self.__args[index]
            if len(self) == 1:  self[0].up()
            

    def __iter__(self):
        if self.type in ('p', 'b'): return iter([self])
        else:                       return iter(self.__args)

    def append(self, *args):
        for arg in args: self.insert(len(self.__args), arg)

    def insert(self, index: int, *args):
        if self.__type not in ('+', '*', '!'): return None
        for arg in args:
            arg = LogicExpression(arg)
            if arg not in self.__args:
                arg.__root = self
                self.__args.insert(index, arg)

    '''Returns the index if it finds the arg referenced, -index if it finds
       an arg equal to the arg provided and None in other case.'''
    def index(self, son:'LogicExpression', p=True)->int:
        if self.type in ('p', 'b'):     return 0 if self[0] == son[0] else -1
        i=0
        while i < len(self) and self[i] is not son: i+=1
        if i != len(self): return i
        if p:
            i=0
            while i < len(self) and self[i] != son: i+=1
            if i != len(self): return -i
        return None
    ##########################################################################
    ##########################################################################
    def take_vars(self):
        if self.type == 'p': self.__vars = [self[0]]
        elif self.type != 'b':
            for l in self:
                for var in l.__vars: 
                    self.__vars += var if var not in self.__vars else []

    def find_vars(self, leafs=[]):
        self.__vars = []
        leafs = self.get_leafs() if len(leafs) == 0 else leafs

        for leaf in leafs:
            if leaf.type == 'p' and leaf[0] not in self.__vars: 
                self.__vars += leaf[0]
        return self.vars

    def get_leafs(self)->list['LogicExpression']:
        leafs = []

        if self.type in ('p', 'b'):    leafs.append(self)

        elif self.type in binary_connectors:
            for l in self:  leafs += l.get_leafs()

        return leafs


    def get_super_leafs(self, leafs:list=[])->list['LogicExpression']:
        leafs = self.get_leafs() if len(leafs) == 0 else leafs
        super_leafs = ls([])

        for l in leafs:
            if not l.isroot():
                super_leafs += l.__root

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

    '''
    If the root provided contains a reference to the objet, root will be changed normally.
    If the root only contains a le equal (logicaly and on his shape) to the objet,
       it will be replaced by self.
    Else, root won't be replaced.'''
    def change_root(self, root:'LogicExpression')->bool:
        
        index = root.index(self)
        if index is not None:
            if index >= 0 : self.__root = root
            else:
                self.__root = root.copy()
                self.__root.__args[-index] = self
        return index is not None

    def change_type(self, value):
        if not {value,self.type} < {'>', '=', '+', '*'}: # if value and type not in those types...
            raise AttributeError(f"type change can't be done between {value} and {self.type}")
        if value in ('>', '=') and len(self) > 2:
            raise AttributeError("implication and biconditional "+ \
                                 f"always  have 2 arguments, it has {len(self)}")
        self.__type = value

    '''if changes is a dictionary, it will change (or add) the specified vars
       if changes is a tuple or list, it will be the new vars'''
    def change_vars(self, changes:dict):
        if type(changes) in (list, tuple) and len(changes) < len(self.__vars): return None

        leafs = self.get_leafs()
        self.find_vars(leafs)
        new_vars = {i:i for i in self.__vars}

        #creates the dictionary whith old_var_name:new_var_name
        if type(changes) == dict:
            self.__vars = list(changes.values())
            new_vars.update(changes)

        elif type(changes) in (list, tuple):
            changes = list(changes)
            self.__vars = changes.copy()
            i=0 #Add each new_var whith new items
            while i<len(changes):
                if changes[i] not in new_vars:
                    for key in new_vars.keys():
                        if key not in changes:
                            new_vars[key] = changes[i]
                i+=1

        #changes the vars from the leafs
        for leaf in leafs: 
            if leaf.type == 'p':
                leaf[0] = new_vars[leaf[0]]
                leaf.take_vars()


    # adds {amount} random vars, default 1
    def add_var(self, amount=1):
        new_len = len(self.vars)+amount
        while len(self.vars) < new_len:
            var = random.choice(variables)
            if var not in self.__vars:  self.__vars += [var]



    # returns two LE with the same vars' list
    def unify(self, other:'LogicExpression', modifying=False) -> tuple:
        if self.__vars == other.__vars : return self, other

        #creates a new le adding necessary vars to compare
        new_self, new_other = self.copy(), other.copy()#there isn't repeated vars
        new_other.__vars  = new_self.__vars = list(set(self.__vars + other.__vars)) 

        if modifying:   self.__vars, other.__vars = new_self.__vars, new_other.__vars

        return ([new_self, new_other])

    def order(self, *order)->list:
        if set(order) >= set(self.__vars): self.__vars = list(order).copy()
        return self.vars


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
        return - LogicExpression(self, other, ltype='=')

    def __sub__(self, other) ->'LogicExpression': return self * -(self*other)

    def __neg__(self) ->'LogicExpression':
        return LogicExpression(self, ltype='!')
    def __invert__(self) ->'LogicExpression': return - self

    #Relational operators
    def __eq__ (self, other:'LogicExpression')->bool:
        if len(self)==1 and self.type==other.type: return self[0] == other[0]
        self, other = self.unify(other)
        return self.minterms() == other.minterms()
    def __ne__ (self, other)->bool:
        return not self == other

    def __contains__(self, other)->bool: return self >= other
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


    def istautology(self)->bool:        return len(self.maxterms()) == 0
    def iscontradiction(self)->bool:    return len(self.minterms()) == 0
    def issatisfacible(self)->bool:     return not self.iscontradiction()
    def isrefutable(self)->bool:        return not self.istautology()
    def iscontingent(self)->bool:       return self.isrefutable() and self.issatisfacible()


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

        self.absorb()

        #REDUCES EACH < TO A >
        if self.type=='<': self.__type, self[0], self[1] = '>', self[1], self[0]

        #simplify 0's and 1's
        self.check_neutral_and_dominant()

    def strange_types(self):
        changes = {'⊕':'=','↛':'>','↑':'*','↓':'+'}
        if self.type in changes.keys(): self.__type = changes[self.type]
        elif self.type == '↚':
            self.__type = '<'
            self[0], self[1] = self[1], self[0]
        else: return None
        self.copy(-self)


    def check_neutral_and_dominant(self):
        if self.type in ('p', 'b'): return None

        if self.type == '!' and self[0].type == 'b':
            self.__init__(not self[0][0], root=self.root)

        elif self.type in ('>', '='):
            if {self[1].type, self[0].type} == {'b'}:
                self.__init__(self("mondongo"), root=self[-1])
            elif {self[1].type, self[0].type} == {'p'} and self[1][0] == self[0][0]:
                self.__init__(1, root=self[-1])
            if self.type == '>' and self[0].type=='b' and self[0][0]==False :
                self.__init__(1, root=self[-1]) #0>alpha = 1
        else:
            i=0
            while i<len(self):
                if self[i].type == 'b':
                    if self.type == '*' and self[i][0] == False:
                        self.__init__(0, root=self[-1]) #a&b&...&0 = 0
                    elif self.type=='+' and self[i][0] == True:
                        self.__init__(1, root=self[-1]) #a&b&...+1 = 1
                    elif (self.__type=='*' and self[i][0]==True) or \
                    (self.__type=='+' and self[i][0]==False):
                            del self[i] #a+0 = a, a*1=a
                            i-=1
                i+=1


    def asociate(self):
        if self.type not in ('+','*'): return None
        i=0
        while i<len(self):
            if self[i].type == self.type:
                self.insert(i+1,*list(self[i]))
                lenght = len(self[i])
                del[self[i]]
                i+=lenght
            else: i+=1


    def distribute(self):
        if not all(l.type in ('+', '*') for l in self) or \
        self.type not in ('+', '*'):                        return None

    def not_not(self):
        if self.type == '!' and self[0].type == '!':
            for i in range(2):  self[0].up()

    def de_morgan(self, full=False):

        if self.type == '!' and self[0].type in ('*','+'):
            self[0].de_morgan()
            self.not_not()

        elif self.type in ('+', '*'):
            self.__type = '+' if self.type == '*' else '*'  # swap(*,+)
            self.__init__(-self, root=self.__root)          #self = not self
            i=0                                             #changes the sign of each arg
            while i < len(self[0]):
                self[0][i] = - self[0][i] 
                i+=1

        if full:
            if self.type == '!': self = self[0] #changes the refference (local change)
            if self.type not in ('*', '+'): return None
            for i in self:
                if i.type=='!':  i.de_morgan(True)
        


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

        if len(args) > 1 or len(args)==1 and type(args[0])!=dict: # le(1,0,...,1)
            vars = {var:value for var,value in zip(self.__vars,args)}
        elif len(args) == 1 and type(args[0]) == dict: vars = args[0]    #it's a dict

        if self.type == 'p': truth = bool(vars[self[0]])
        elif self.type == 'b': truth = bool(self[0])
        elif self.type == '!': truth = not bool(self[0](vars))
        else:
            truth_list = [e(vars) for e in self] #TURNS each argument INTO A BOOL VALUE
            if self.type == '*':
                truth = True
                for t in truth_list: truth &= t
            elif self.type == '+':
                truth = False
                for t in truth_list: truth |= t
            elif self.type == '>':
                truth = (not truth_list[0]) or truth_list[1]
            elif self.type == '=':
                truth = ((truth_list[0]) and truth_list[1]) or \
                        ((not truth_list[1]) and not truth_list[0])

        return (1 if truth else 0)


    def truth_board(self)->tuple:
        board = []
        minterms = self.minterms()
        values = [True if i in minterms else False for i in range(2**len(self.vars))]
        for bit in range(2**len(self.vars)):
            board += [(dec_binbol(bit,len(self.vars)), values[bit])]
        return (tuple(self.vars), tuple(board))

    ###########################################################################

    def to_canonical_shape(self,on_minterms=True)->'LogicExpression':
        if self.type == 'b': return self.copy()
        
        result, num_vars = [] , len(self.vars) #a simple optimization

        minterms = tuple(self.minterms())
        maxterms = tuple(set(range(2**num_vars)) - set(minterms))
        terms = minterms if on_minterms else maxterms
        symbol = '*' if on_minterms else '+'

        for dec in terms:
            binary = dec_binbol(dec,num_vars)

            string = ""
            i=0
            for bit in binary:
                if (on_minterms and not bit) or (not on_minterms and bit):
                    oposite = '!'
                else: oposite = ''
                string += oposite + self.vars[i] + symbol
                i += 1
            string = '('+string[:-1]+')'

            result.append(LogicExpression(string))

        symbol = '*' if symbol=='+' else '+'
        return LogicExpression(*result, ltype=symbol) if len(result) > 0 else self.copy()



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
        terms, num_vars = [], len(self.__vars)  # simple optimization
        for bit in range(2**num_vars):
            truth = self(*dec_binbol(bit,num_vars))
            if (on_minterms and truth) or (not on_minterms and not truth): 
                terms.append(bit)
        return set(terms)
    
    def to_clauses(self):

        self = self.copy()

        self.to_boolean_logic()

        lset = ls()


        return lset


    ###########################################################################



    #CASTING##################################################################

    def __bool__(self)->bool: return self.istautology()

    def __str__(self)->str:
        string = ""

        if self.type in binary_connectors:
            for l in self:  
                if l.type in ('p', 'b') or (l.type == '!' and l[0].type == 'p'): 
                    string += str(l) + ' ' + self.type + ' '
                else: string += '('+str(l)+')' + ' ' + self.type + ' '
            string = string[:-3] # removes the last connective

        elif self.type == '!':
            if self[0].type == 'b': string+= str(int(not bool(self[0][0])))
            elif self[0].type == 'p': string += self.type + str(self[0])
            else:   string += self.type + '('+str(self[0])+')'

        elif self.type in ('p','b'):
            string += self[0] if self.type == 'p' else str(int(self[0]))

        #changes notation
        for old, new in notation_out.items():  string = string.replace(old, new)

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
        if other == []: return ls(*(LogicExpression(c,c[-1]) for c in self))
        else:
            self.clear()
            self.extend(other.copy())
            return self



