from ..asdl import basic, expr, pattern, typ, match, NativeType, equals
from ..utils import make_overload
from typing import overload
import numpy as np

_undef = object()


class Object:

    def __init__(self, value, ty):
        self.value = value
        self.type = ty


@make_overload
def visit(asdl, local: dict, glob: dict):
    return type(asdl)


@overload
def visit(asdl: basic.Number, local: dict, glob: dict):
    return Object(asdl.num, asdl.type)


@overload
def visit(a: basic.Symbol, local: dict, glob: dict):
    if a.value in local:
        return Object(local[a.value], get_type(local, a.value))

    try:
        return Object(glob[a.value], get_type(glob, a.value))
    except KeyError:
        raise NameError(f"``{a.value}``")


@overload
def visit(a: basic.String, local: dict, glob: dict):
    return Object(a.value, NativeType.s)


@overload
def visit(a: basic.Const.false, local: dict, glob: dict):
    return Object(False, bool)


@overload
def visit(a: basic.Const.true, local: dict, glob: dict):
    return Object(True, bool)


@overload
def visit(a: basic.Const.nil, local: dict, glob: dict):
    return Object(True, None)


@overload
def visit(a: expr.Accessor, local: dict, glob: dict):
    v: Object = visit(a.value, local, glob)
    ty, value = v.type, v.value
    for each in a.attributes:
        attr = each.value
        if isinstance(ty, (typ.DiscriminateUnionType, typ.ArrayType, typ.TupleType, typ.LinkedListType)):
            name = ty.sig.name
            raise AttributeError(f"Cannot access attribute `{name}`. {loc_to(each)}")

        elif isinstance(ty, typ.RecordType):

            idx, attr_ty = ty.index_attr(attr)
            if idx is -1:
                name = ty.sig.name
                raise AttributeError(f"Record type `{name}` has no attribute `{attr}`. {loc_to(each)}")
            value = value[idx]
            ty = attr_ty

        elif ty is object:
            value = getattr(value, attr)
        else:
            attr_getter = ty.__dict__.get(attr, _undef)
            if attr_getter is _undef:
                raise AttributeError(f"Basic Type `{ty.__name__}` has no attribute `{attr}`. {loc_to(each)}")
            value = attr_getter(value)
            ty = object

    return Object(v, ty)


@overload
def visit(a: expr.ArrayLiteral, local: dict, glob: dict):
    arr = tuple(visit(e, local, glob) for e in a.elements)
    if not arr:
        return Object(np.array([]), typ.ArrayType(a.lineno, a.colno, object))

    _ty = arr[0].type
    ty = _ty if all(equals(e.type, _ty) for e in arr) else object
    return Object(np.array(tuple(e.value for e in arr)), typ.ArrayType(a.lineno, a.colno, ty))


@overload
def visit(a: expr.TupleLiteral, local: dict, glob: dict):
    arr = tuple(visit(e, local, glob) for e in a.elements)
    return Object(tuple(e.value for e in arr), tuple(e.type for e in arr))


@overload
def visit(a: expr.ListLiteral, local: dict, glob: dict):
    arr = [visit(e, local, glob) for e in a.elements]

    if not arr:
        return Object((), typ.LinkedListType(a.lineno, a.colno, object))

    _ty = arr[0].type
    ty = _ty if all(equals(e.type, _ty) for e in arr) else object
    return Object([e.value for e in arr], typ.LinkedListType(a.lineno, a.colno, ty))


@overload
def visit(a: expr.RecordLiteral, local: dict, glob: dict):
    attrs = tuple(e.key for e in a.elements)

    if not attrs:
        return Object([], typ.RecordType(a.lineno, a.colno, object, ()))

    ty: typ.RecordType = get_record_type(glob, attrs)

    if not ty:
        raise TypeError(f"Such record type with attributes: {attrs}. {loc_to(a)}")

    arr = [visit(e.value, local, glob) for e in a.elements]

    return Object([e.value for e in arr], ty)


@overload
def visit(a: expr.Index, local: dict, glob: dict):
    v = visit(a.value, local, glob)
    value = v.value
    ty = v.type
    if isinstance(ty, (typ.DiscriminateUnionType, typ.RecordType)):
        raise TypeError

    elif isinstance(ty, typ.TupleType):
        raise NotImplementedError

