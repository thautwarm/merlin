from rml.analysis.ctx import Context, SymTable
from Redy.Magic.Classic import execute
from Redy.Magic.Pattern import Pattern
from Redy.Opt.ConstExpr import macro, optimize, constexpr, const
from typing import overload
from rml.asdl import basic, expr, match, pattern, type as typ
from rml.compiler.bc import bc, build_inst
import types


@Pattern
def visit(asdl, ctx):
    return type(asdl)


def overloader(pat_func):
    def call(reg_func: 'function'):
        k, v = next(iter(reg_func.__annotations__.items()))
        return pat_func.case(v)(reg_func)

    return call


globals()['overload'] = overloader(visit)


@overload
@optimize
def visit(asdl: basic.Symbol, ctx: Context):
    @macro
    def branch(obj: SymTable, inst):
        idx = obj.get_index(asdl.value)
        if idx is not -1:
            codes = build_inst(inst, idx)
            ctx.codes_update(asdl, codes)
            return

    branch(ctx.local, bc['LOAD_FAST'])
    branch(ctx.glob, bc['LOAD_GLOBAL'])
    branch(ctx.closure, bc['LOAD_DEREF'])
    raise NameError
