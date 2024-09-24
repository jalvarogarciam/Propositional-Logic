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



    def __getitem__(self,index:int)->'LogicFunction': 
        return super().__getitem__(index).copy()

    def __setitem__(self, index, value):
        if type(index) == slice: raise TypeError('slicing is not allowed')
        if index < 0: raise IndexError('root assignment is not allowed')

        if self.type in ('p', 'b'): self.__args = value #for p, b
        else: 
            self.__args[index] = value.copy(mode='i') #for ! + * >
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