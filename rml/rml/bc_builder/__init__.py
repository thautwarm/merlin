from typing import NamedTuple
from Redy.Magic.Classic import record
from enum import Enum
import opcode
from rml.compiler.bc import bc

globals()['NamedTuple'] = object


def build_inst(op, arg):
    if arg is 0:
        return [(op, arg)]

    b = [(op, arg & 0xff)]
    while arg > 0xff:
        arg >>= 8
        b.append((opcode.EXTENDED_ARG, arg & 0xff))
    b.reverse()
    return b


class Ctx(Enum):
    LOCAL = 1
    GLOBAL = 2
    NONLOCAL = 3
    CONST = 4


class ASDL:
    lineno: int  # lineno and colno are both that of source codes!!
    colno: int

    def build(self):
        pass


@record
class Label(ASDL, NamedTuple):
    lineno: int
    colno: int


class Manage:
    @record
    class LOAD(ASDL, NamedTuple):
        lineno: int
        colno: int

        name: str
        ctx: Ctx

        def build(self: 'ASDL.LOAD', ctx):
            ctx.set_lnotab(self.lineno)
            (ctx.local_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['LOAD_FAST'], idx)))

             .closure_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['LOAD_DEREF'], idx)))

             .global_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['LOAD_GLOBAL'], idx)))

             .const_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['LOAD_CONST'], idx))))

    @record
    class Store(ASDL, NamedTuple):
        lineno: int
        colno: int

        name: str
        ctx: Ctx

        def build(self: 'ASDL.Store', ctx):
            ctx.set_lnotab(self.lineno)
            (ctx.local_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['STORE_FAST'], idx)))

             .closure_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['STORE_DEREF'], idx)))

             .global_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['STORE_GLOBAL'], idx))))

    @record
    class Delete(ASDL, NamedTuple):
        lineno: int
        colno: int

        name: str
        ctx: Ctx

        def build(self: 'ASDL.Delete', ctx):
            ctx.set_lnotab(self.lineno)
            (ctx.local_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['DELETE_FAST'], idx)))

             .closure_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['DELETE_DEREF'], idx)))

             .global_find(self.name).if_not_none(lambda idx: ctx.append_code(build_inst(bc['DELETE_GLOBAL'], idx))))


class Operator:
    @record
    class Neg(ASDL, NamedTuple):
        lineno: int
        colno: int

        value: ASDL

        def build(self):
            self.value.build()


    @record
    class Not(ASDL, NamedTuple):
        lineno: int
        colno: int

        value: ASDL

    @record
    class Invert(ASDL, NamedTuple):
        lineno: int
        colno: int

        value: ASDL

    @record
    class Power(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class Mul(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class MatMul(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class Div(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class Modulo(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class Sub(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class Slice(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class LShift(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class RShift(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class And(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL

    @record
    class Or(ASDL, NamedTuple):
        lineno: int
        colno: int

        left: ASDL
        right: ASDL


class Expr:
    @record
    class BuildList(ASDL, NamedTuple):
        lineno: int
        colno: int

        xs: tuple

    @record
    class BuildTuple(ASDL, NamedTuple):
        lineno: int
        colno: int

        xs: tuple

    @record
    class BuildMap(ASDL, NamedTuple):
        lineno: int
        colno: int

        values: tuple
        key: ASDL

    @record
    class BuildSet(ASDL, NamedTuple):
        lineno: int
        colno: int

        xs: tuple


@record
class GetIter(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: ASDL


class Control:
    @record
    class Return(ASDL, NamedTuple):
        lineno: int
        colno: int

    @record
    class JumpIf(ASDL, NamedTuple):
        lineno: int
        colno: int

        cond: ASDL

    @record
    class JumpTo(ASDL, NamedTuple):
        lineno: int
        colno: int

        who: ASDL

    @record
    class WithCleanUp(ASDL, NamedTuple):
        lineno: int
        colno: int

        inner: ASDL

    @record
    class Call(ASDL, NamedTuple):
        lineno: int
        colno: int

        Fn: ASDL
        Args: tuple
