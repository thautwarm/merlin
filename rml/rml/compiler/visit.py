from ..utils import make_overload
from Redy.Magic.Pattern import Pattern
from Redy.Opt.ConstExpr import macro, optimize, constexpr, const
from typing import overload

from rml.analysis.ctx import Context, SymTable, ModuleDef
from rml.asdl import basic, expr, match, pattern, typ as typ
from rml.compiler.bc import bc, build_inst
from rml.compiler.cr import Compiler
import types

numpy_array_fn_name = '.rml.nparr'
linked_list_cons_name = '.rml.lstc'


@make_overload
def visit(asdl: basic.ASDL, ctx, cr):
    return type(asdl)


@overload
def visit(asdl: basic.ASDL, ctx, cr):
    """
    for hinting
    """


@overload
@optimize
def visit(asdl: basic.Symbol, ctx: Context, cr: Compiler):
    name = asdl.to_name()

    @macro
    def _do_stuff(sb, inst):
        idx = sb.get_index(name)
        if idx is not -1:
            cr.add_inst(inst, idx, asdl.lineno)
            return

    _do_stuff(ctx.symtable, bc['LOAD_FAST'])
    _do_stuff(ctx.closure, bc['LOAD_FAST'])
    _do_stuff(ctx.glob, bc['LOAD_GLOBAL'])

    raise NameError(name)


@overload
@optimize
def visit(asdl: basic.Number, ctx: Context, cr: Compiler):
    idx = cr.index_consts(asdl.num)
    cr.add_inst(bc['LOAD_CONST'], idx, asdl.lineno)


@overload
@optimize
def visit(asdl: basic.String, ctx: Context, cr: Compiler):
    idx = cr.index_consts(asdl.value)
    cr.add_inst(bc['LOAD_CONST'], idx, asdl.lineno)


@overload
@optimize
def visit(asdl: basic.Const.nil, ctx: Context, cr: Compiler):
    idx = cr.index_consts(None)
    cr.add_inst(bc['LOAD_CONST'], idx, asdl.lineno)


@overload
@optimize
def visit(asdl: basic.Const.true, ctx: Context, cr: Compiler):
    idx = cr.index_consts(True)
    cr.add_inst(bc['LOAD_CONST'], idx, asdl.lineno)


@overload
@optimize
def visit(asdl: basic.Const.false, ctx: Context, cr: Compiler):
    idx = cr.index_consts(False)
    cr.add_inst(bc['LOAD_CONST'], idx, asdl.lineno)


@overload
@optimize
def visit(asdl: expr.ArrayLiteral, ctx: Context, cr: Compiler):
    lineno = asdl.lineno
    elements = asdl.elements
    cr.add_inst(bc['LOAD_GLOBAL'], ctx.glob.get_index(constexpr[numpy_array_fn_name]), lineno)

    if not all(map(is_constant, elements)):
        for each in elements:
            visit(each, ctx, cr)
        cr.add_inst(bc['BUILD_TUPLE'], len(elements), lineno)
    else:
        tp: tuple = create_constant_tuple(elements)
        idx = cr.index_consts(tp)
        cr.add_inst(bc['LOAD_CONST'], idx, lineno)

    cr.add_inst(bc['CALL_FUNCTION'], 1, lineno)


@overload
@optimize
def visit(asdl: expr.ListLiteral, ctx: Context, cr: Compiler):
    lineno = asdl.lineno

    # List Tail is Nil
    idx = cr.index_consts(None)
    cr.add_inst(bc['LOAD_CONST'], idx, lineno)

    for each in asdl.elements:
        visit(each, ctx, cr)
        cr.add_inst(bc['BUILD_TUPLE'], 2, lineno)


@overload
@optimize
def visit(asdl: expr.TupleLiteral, ctx: Context, cr: Compiler):
    elements = asdl.elements

    for each in elements:
        visit(each, ctx, cr)

    cr.add_inst(bc['BUILD_TUPLE'], len(elements), asdl.lineno)


@overload
@optimize
def visit(asdl: expr.Accessor, ctx: Context, cr: Compiler):
    visit(asdl.value, ctx, cr)
    for each in asdl.attributes:
        name, lineno = each.value, each.lineno
        cr.add_inst(bc['LOAD_ATTR'], cr.index_names(each.value), lineno)


@overload
@optimize
def visit(asdl: expr.Index, ctx: Context, cr: Compiler):
    visit(asdl.value, ctx, cr)
    for each in asdl.items:
        visit(each, ctx, cr)
        cr.add_inst(bc['BINARY_SUBSCR'], cr.index_names(each.value), each.lineno)


@overload
@optimize
def visit(asdl: expr.IndexItem, ctx: Context, cr: Compiler):
    items = asdl.items
    n = len(items)
    if n is 1:
        visit(items[0], ctx, cr)
        return
    for each in items:
        visit(each, ctx, cr)
    cr.add_inst(bc['BUILD_TUPLE'], n, asdl.lineno)


@overload
@optimize
def visit(asdl: expr.Slice, ctx: Context, cr: Compiler):
    visit(asdl.start, ctx)
    if not asdl.end:
        cr.add_inst(bc['LOAD_CONST'], cr.index_consts(None), asdl.lineno)  # set lineno to 0 for speeding up is ok?
        cr.add_inst(bc['BUILD_SLICE'], 2, asdl.lineno)
        return

    visit(asdl.end, ctx, cr)
    if not asdl.sep:
        cr.add_inst(bc['BUILD_SLICE'], 2, asdl.lineno)
        return

    visit(asdl.sep, ctx, cr)
    cr.add_inst(bc['BUILD_SLICE'], 3, asdl.lineno)


@overload
@optimize
def visit(asdl: expr.For, ctx: Context, cr: Compiler):
    lineno = asdl.lineno
    colno = asdl.colno
    collection = asdl.collection
    # load map

    # test the type of collection in compiling time, if linkedlist, use ".lmap"

    cr.add_inst(bc['LOAD_GLOBAL'], ctx.glob.get_index('.map'), lineno)

    # load foreach-fn
    visit(expr.Lambda(lineno, colno, asdl.pat, asdl.stuff), ctx, cr)

    # load collection
    visit(asdl.collection, ctx, cr)

    # yield from map(foreach-fn, collection)
    cr.add_inst(bc['CALL_FUNCTION'], 2, lineno)


@overload
@optimize
def visit(asdl: expr.Lambda, ctx: Context, cr: Compiler):
    # cr.add_inst(bc['LOAD_CONST'], cr.index_consts(make_function(asdl.pat, asdl.stuff, ctx.create_sub(), cr)), asdl.lineno)

    raise NotImplemented


def make_function(pat: pattern.Pattern, stuff: tuple, ctx: Context, cr: Compiler) -> types.CodeType:
    raise NotImplemented


@overload
@optimize
def visit(asdl: ModuleDef, ctx: Context, cr: Compiler):
    for each in asdl.stuff:
        visit(each, ctx, cr)


"""

type TailRec = TailRec f args
let rec f = tailrec fn 
                | LessThan0   -> 1 
                | MoreThan1 x -> 1 + fn (x - 1)





tail = tailrec(f)(arg) 
stack = [tail]
result = None
while True:
    
    try:
        e = tail.send(result)
    except StopIteration:
        try:
            stack.pop()
        except StopIteration:
            break
        tail = stack[-1]
        continue
        
    if e.__class__ is tailrec:
        f, arg = e
        e = f(arg)
        
        if e.__class__ is generator:
            tail = e
            stack.append(tail)
        else:
            
        e = result
        result = None
        continue
    
    result = e.send(result)  
    
    stack.pop()
    if not stack:
        break




        
    
    




"""
