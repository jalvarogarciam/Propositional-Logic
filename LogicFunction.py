from LogicExpression import LogicExpression as le



class LogicFunction(le):
    '''
    The shape of LogicExpression's are like a "tree of expressions" where each one
    is connected with its leafs and its root. 
    The types allowed are Unary(!) or Binary Connective(+,*,>,=), a proposition(p), 
    or a bool(b). 
    '''
    ##########################################################################
    '''
    Builds a new Logic Expression with the args provided.
        -if ltype is specified, args will be understood as a list of LogicExpressions
        -if order is specified, it will be the vars' list
        -if root is provided, it will be the instance's root if self is a part of
        its argument.
    '''
    def __init__(self, *args, ltype='', root:le = None, order:tuple=None):
        super().__init__(*args, ltype=ltype, root=root, order=order)
        if len(args) > 0 and type(args[0])==str or ltype != '': self.properties()


    def __getitem__(self,index:int)->'LogicFunction': 
        return super().__getitem__(index).copy()
    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self.properties()

    def __iter__(self):
        if self.type in ('p', 'b'): return iter([self.copy()])
        else:                       return iter(self.__args.copy())

    def append(self, *args):
        for arg in args: self.insert(len(self.__args), arg)
    def insert(self, index: int, *args):
        for arg in args: 
            if arg not in list(self): super().insert(index, arg)





    # returns two LE with the same vars' list
    def unify(self, other:le, modifying=False) -> tuple:
        if self.__vars == other.__vars : return self, other

        #creates a new le adding necessary vars to compare
        new_self, new_other = self.copy(), other.copy()#there isn't repeated vars
        new_other.__vars  = new_self.__vars = list(set(self.__vars + other.__vars)) 

        if modifying:   self.__vars, other.__vars = new_self.__vars, new_other.__vars

        return ([new_self, new_other])

    ###########################################################################
    #OPERATORS
    ###########################################################################
    #Arithmetic operators
    def __add__(self, other) ->le:
        return le(self, other, ltype='+')
    def __or__(self, other) ->'le': return self + other

    def __mul__(self, other) ->'le':
        return le(self, other, ltype='*')
    def __and__(self, other) ->'le': return self * other

    def __xor__(self, other) ->'le':
        return - le(self, other, ltype='=')

    def __sub__(self, other) ->'le': return self * -(self*other)

    def __neg__(self) ->'le':
        return le(self, ltype='!')
    def __invert__(self) ->'le': return - self

    #Relational operators
    def __eq__ (self, other:'le')->bool:
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
    



    ###########################################################################



    #CASTING##################################################################

    def __bool__(self)->bool: return self.istautology()