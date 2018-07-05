from Redy.Magic.Classic import cache
from Redy.Opt.ConstExpr import optimize, const

from .basic import *
from .pattern import Pattern
from ..utils import make_overload
from typing import Dict, overload

_not_found = object()


@record
class TypeSig(ASDL, NamedTuple):
    lineno: int
    colno: int

    name: str
    type_spec: Tuple['TypeSigImp']


@record
class TupleType(ASDL, NamedTuple):
    lineno: int
    colno: int

    elements: Tuple['TypeSigImp']


@record
class Undecided(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: str
    refine: Symbol


TypeSigImp = Union[TypeSig, TupleType, Undecided]


@record
class FieldDecl(ASDL, NamedTuple):
    lineno: int
    colno: int

    name: str
    sig: TypeSigImp


@record
class ADT(ASDL, NamedTuple):
    lineno: int
    colno: int

    tag: Symbol
    cons: TypeSigImp


@record
class DiscriminateUnionType(ASDL, NamedTuple):
    lineno: int
    colno: int

    sig: TypeSig
    cons: Tuple[ADT, ...]

    def loc(self, idx: int):
        return self.cons[idx]


DiscriminateUnionDef = DiscriminateUnionType


@record
class RecordType(ASDL, NamedTuple):
    lineno: int
    colno: int

    sig: TypeSig
    fields: Tuple[FieldDecl, ...]

    @cache
    def index_attr(self, attr: str):
        for idx, each in enumerate(self.fields):
            if each.name == attr:
                return idx, each.sig
        return -1, None


@record
class ArrayType(ASDL, NamedTuple):
    lineno: int
    colno: int

    ty: TypeSig


RecordDef = RecordType


@record
class Annotation(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: ASDL
    sig: TypeSig


@record
class LinkedListType(ASDL, NamedTuple):
    lineno: int
    colno: int

    ty: TypeSig


"""

let f = fn x -> x <: 



G : f
 


type F of 'a = 
    | F  'a * F of 'a 
 
"""
