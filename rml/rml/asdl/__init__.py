from .match import *
from .pattern import *
from .typ import *
from .expr import *


@record
class ModuleDef(ASDL, NamedTuple):
    lineno: int
    colno: int

    name: Symbol
    stuff: Tuple[ASDL, ...]


@make_overload
def equals(self, other):
    return type(self)


@overload
def equals(self: any, other: any):
    if not isinstance(other, ASDL):
        return self == other

    if self.__annotations__ is not other.__annotations__:
        return False
    return all(map(lambda key: equals(getattr(self, key), getattr(other, key)),
                   (key for key in self.__annotations__ if key not in ('lineno', 'colno'))))


@overload
def equals(self: tuple, other: tuple):
    if not isinstance(other, tuple):
        return False
    return all(map(equals, self, other))


equals = discrete_cache(equals)
