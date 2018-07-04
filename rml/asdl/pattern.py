from .basic import *

globals()['NamedTuple'] = object

Pattern = Union[
    'ConsPattern', 'ListPattern', 'TuplePattern', 'RecordPattern', 'ADTPattern', 'NamePattern', 'LiteralExpr']


@record
class PatternPair(ASDL, NamedTuple):
    lineno: int
    colno: int

    key: str
    value: 'Pattern'


@record
class ConsPattern(ASDL, NamedTuple):
    lineno: int
    colno: int

    head: Pattern
    tail: 'ConsPattern'


@record
class ListPattern(ASDL, NamedTuple):
    lineno: int
    colno: int

    elements: Tuple[Pattern, ...]


@record
class TuplePattern(ASDL, NamedTuple):
    lineno: int
    colno: int

    elements: Tuple[Pattern, ...]


@record
class RecordPattern(ASDL, NamedTuple):
    lineno: int
    colno: int
    elements: Tuple[PatternPair, ...]


@record
class ADTPattern(ASDL, NamedTuple):
    lineno: int
    colno: int

    tag: ...
    pattern_list: Tuple[Pattern, ...]


@record
class NamePattern(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: str


@record
class LiteralExpr(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: ...
