from Redy.Magic.Pattern import Pattern
from Redy.Opt.ConstExpr import optimize, const
from ..asdl import typ
from ..asdl.typ import *
from typing import overload

_not_found = object()


@make_overload
def decide(asdl, type_trans_map, type_qualifier):
    return type(asdl)


@overload
def decide(core: TypeSig, type_trans_map: Dict[object, TypeSig], type_qualifier: Dict[str, object]):
    return TypeSig(core.lineno, core.colno, core.name,
                   tuple(decide(e, type_trans_map, type_qualifier) for e in core.type_spec))


@overload
def decide(core: TupleType, type_trans_map: Dict[object, TypeSig], type_qualifier: Dict[str, object]):
    return TupleType(core.lineno, core.colno,
                     tuple(decide(e, type_trans_map, type_qualifier) for e in core.elements))


@overload
@optimize
def decide(core: Undecided, type_trans_map: Dict[object, TypeSig], type_qualifier: Dict[str, object]):
    not_found: const = _not_found
    obj = type_qualifier.get(core.value, not_found)
    if obj is not_found:
        return core
    ty = type_trans_map[obj]

    # USE RUNTIME RML TO REFINE

    if ml_eval(core.refine)(ty):
        raise TypeError(f"At file: line {core.lineno}, column {core.colno}, refine `{core.value}` failed.")

    return ty


@overload
def decide(core: FieldDecl, type_trans_map: Dict[object, TypeSig], type_qualifier: Dict[str, object]):
    ty = decide(core.sig, type_trans_map, type_qualifier)
    if ty is core.sig:
        return core
    return FieldDecl(core.lineno, core.colno, core.name, ty)


@overload
def decide(core: ADT, type_trans_map: Dict[object, TypeSig], type_qualifier: Dict[str, object]):
    ty = decide(core.cons, type_trans_map, type_qualifier)
    if ty is core.cons:
        return core
    return ADT(core.lineno, core.colno, core.tag, ty)
