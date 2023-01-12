import builtins
from enum import Enum


def coerce_type(self, O, T: type, require: bool = False):
    if not isinstance(T, type):
        T = type(T)
    if type(O) is T or T is type(None):
        return O
    if isinstance(T, type(Enum)):
        # Enum(Item) returns the enum member corresponding to the value
        #  ie. for Example(Enum): A=1, Example(1) will return Example.A
        #  and Example('A') will throw a ValueError
        try:
            return T(O)
        except ValueError:
            # Enum[Item] returns the enum member corresponding to the name
            #  ie. for Example(Enum): A=1, Example['A'] will return Example.A
            #  and Example[1] will throw a KeyError
            try:
                return T[O]
            except KeyError:
                # If we reach this point, there is no possibility of automatically turning `O` into
                # a member of the given Enum.
                return None
    match T:
        case builtins.bool:
            # Have to cast O to string, because O could be anything. Goodness, what if it were an int?
            return str(O).lower() in ("true", "t", "yes", "1")
        case _:
            R = None
            try:
                R = T(O)
            except:
                if not require:
                    R = O
            finally:
                return R
