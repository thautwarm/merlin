from .basic import *
from .pattern import Pattern


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

    value: Symbol
    refine: Symbol


TypeSigImp = Union[TypeSig, Tuple, Undecided]


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
class DiscriminateUnionDef(ASDL, NamedTuple):
    lineno: int
    colno: int

    sig: TypeSig
    cons: Tuple[ADT, ...]


@record
class RecordDef(ASDL, NamedTuple):
    lineno: int
    colno: int

    sig: TypeSig
    fields: Tuple[FieldDecl, ...]


@record
class Annotation(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: ASDL
    sig: TypeSig


class LinkedListType:
    pass
