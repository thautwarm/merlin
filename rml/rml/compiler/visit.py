# from singledispatch import singledispatch
from Redy.Magic.Classic import execute
from Redy.Magic.Pattern import Pattern
from Redy.Opt.ConstExpr import macro, optimize, constexpr, const
from typing import overload
from rml.asdl import basic, expr, match, pattern, type as typ
from rml.compiler.bc import bc, build_inst


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
def visit(asdl: basic.Symbol, ctx):
    @macro
    def branch(obj, inst):
        if obj.find(asdl.value):
            idx = obj.get(asdl.value)
            codes = build_inst(inst, idx)
            ctx.codes_update(asdl, codes)
            return

    branch(ctx.local, bc['LOAD_FAST'])
    branch(ctx.glob, bc['LOAD_GLOBAL'])
    branch(ctx.closure, bc['LOAD_DEREF'])
    raise NameError


@overload
@optimize
def visit(asdl: basic.Number, ctx):
    ctx.consts.add(asdl.num)

    @macro
    def branch(obj, inst):
        if obj.find(asdl.value):
            idx = obj.get(asdl.value)
            codes = build_inst(inst, idx)
            ctx.codes_update(asdl, codes)
            return

    branch(ctx.consts, bc['LOAD_CONST'])
    raise ValueError


@overload
@optimize
def visit(asdl: basic.String, ctx):
    ctx.consts.add(asdl.value)

    @macro
    def branch(obj, inst):
        if obj.find(asdl.value):
            idx = obj.get(asdl.value)
            codes = build_inst(inst, idx)
            ctx.codes_update(asdl, codes)
            return

    branch(ctx.consts, bc['LOAD_CONST'])
    raise ValueError


_keys = {
    basic.Const.true: True, basic.Const.false: False, basic.Const.nil: None
}


#
# class C:
#     class consts:
#         add = lambda x: print(x)
#
#         find = lambda x: True
#
#         get = lambda x: 1
#
#     update_lineno_lnotab = lambda x, y: print(x, y)
#


@overload
def visit(asdl: basic.Const.false, ctx): ...


@overload
def visit(asdl: basic.Const.true, ctx): ...


@overload
def visit(asdl: basic.Const.nil, ctx): ...


for k, v in _keys.items():
    @overload
    @optimize
    def visit(asdl: k, ctx):
        value: const = v
        ctx.consts.add(value)

        @macro
        def branch(obj, inst):
            if obj.find(value):
                idx = obj.get(value)
                codes = build_inst(inst, idx)
                ctx.codes_update(asdl, codes)
                return

        branch(ctx.consts, bc['LOAD_CONST'])
        raise ValueError


@overload
@optimize
def visit(asdl: expr.Accessor, ctx):
    indices = ctx.names.add_many(asdl.attributes)
    visit(asdl.value, ctx)
    for idx in indices:
        codes = build_inst(bc['LOAD_ATTR'], idx)
        ctx.codes_update(asdl, codes)


@overload
def visit(asdl: expr.ArrayLiteral, ctx):
    # load np.ndarray
    ctx.glob.add('.ml.ndarr')
    idx = ctx.glob.get('.ml.ndarr')
    codes = build_inst(bc['LOAD_GLOBAL'], idx)

    # make array literal
    for each in asdl.elements:
        visit(each, ctx)
    n = len(asdl.elements)
    codes += build_inst(bc['BUILD_LIST'], n)

    # apply np.array on list literal
    codes += build_inst(bc['CALL_FUNCTION'], 1)

    ctx.codes_update(asdl, codes)
