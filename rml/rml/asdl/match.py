from .basic import *


@record
class Case(ASDL, NamedTuple):
    lineno: int
    colno: int

    pattern: ASDL
    stuff: ASDL
    when: ASDL


@record
class Match(ASDL, NamedTuple):
    lineno: int
    colno: int

    expr: ASDL

    cases: Tuple[Case, ...]


@record
class LambdaCases(ASDL, NamedTuple):
    lineno: int
    colno: int

    cases: Tuple[Case, ...]
