from .match import *
from .pattern import *
from .type import *
from .expr import *


@record
class ModuleDef(ASDL, NamedTuple):
    lineno: int
    colno: int

    name: Symbol
    stuff: Tuple[ASDL, ...]
