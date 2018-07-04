from .basic import *
from .pattern import Pattern


@record
class FunctionCall(ASDL, NamedTuple):
    lineno: int
    colno: int

    s_expr: Tuple[ASDL, ...]


@record
class Accessor(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: ASDL
    attributes: Tuple[Symbol, ...]


@record
class IndexItem(ASDL, NamedTuple):
    lineno: int
    colno: int

    items: Tuple[ASDL, ...]


@record
class Slice(ASDL, NamedTuple):
    lineno: int
    colno: int

    start: ASDL
    end: ASDL
    sep: ASDL


@record
class Index(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: ASDL
    items: Tuple[IndexItem, ...]


@record
class For(ASDL, NamedTuple):
    lineno: int
    colno: int

    pat: 'Pattern'
    collection: ASDL
    stuff: ASDL
    return_value: bool


@record
class Lambda(ASDL, NamedTuple):
    lineno: int
    colno: int

    args: Tuple['Pattern', ...]

    stuff: ...


@record
class BinOprSeq(ASDL, NamedTuple):
    lineno: int
    colno: int

    seq: Tuple[T, ...]


if "Four Literal":
    @record
    class ListLiteral(ASDL, NamedTuple):
        lineno: int
        colno: int

        elements: Tuple[ASDL, ...]


    @record
    class TupleLiteral(ASDL, NamedTuple):
        lineno: int
        colno: int

        elements: Tuple[ASDL, ...]


    @record
    class ArrayLiteral(ASDL, NamedTuple):
        lineno: int
        colno: int

        elements: Tuple[ASDL, ...]


    @record
    class ExprPair(ASDL, NamedTuple):
        lineno: int
        colno: int

        key: str
        value: 'Expr'


    @record
    class RecordLiteral(ASDL, NamedTuple):
        lineno: int
        colno: int
        elements: Tuple[ExprPair, ...]
