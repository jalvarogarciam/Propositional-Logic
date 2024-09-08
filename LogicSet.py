from LogicExpression import LogicExpression as le

class ls:
    def __init__(self, *args):
        
        self.__clauses : list = []

        if len(args) == 0: ...

        elif type(args[0]) == ls:
            self.__clauses = args[0].__clauses.copy()

        elif type(args[0]) != le and len(args) == 1: self.__clauses = list(args[0])

        else : self.__clauses = list(args)


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



lis = ls(le("!d+s"))
los = ls(le("d+s"))
lis += los
print(lis+los)