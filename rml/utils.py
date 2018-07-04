from rbnf.Tokenizer import Tokenizer
from rbnf.State import State
from typing import Sequence, Optional
import operator
import types
from .asdl import *

_undef = object()


def _get_key(value: dict, k, default_factory):
    v = value.get(k, _undef)
    if v is _undef:
        return default_factory(k)
    return v


def template(func: types.FunctionType):
    def default_set(**default_kwds):
        def call(*args, **kwargs):
            args = iter(args)

            def _default_get(k):
                v = default_kwds.get(k, _undef)
                if v is _undef:
                    return next(args)
                return v
            return func(*args, **{k: _get_key(kwargs, k, _default_get) for k in func.__code__.co_varnames[:func.__code__.co_argcount]})

        def drop(_):
            return call

        return drop

    return default_set


@template
def check_indent(state: State, tokens: Sequence[Tokenizer], last: Tokenizer, how):
    if last is _undef:
        try:
            last = tokens[state.end_index - 1]
        except IndexError:
            return True

    elif last is None:
        return True

    try:
        tk = tokens[state.end_index]
    except IndexError:
        return False
    return how(tk.colno, last.colno)


def check_not_new_line(state: State, tokens: Sequence[Tokenizer], last: Tokenizer = _undef):
    if last is _undef:
        try:
            last = tokens[state.end_index - 1]
        except IndexError:
            return True

    elif last is None:
        return True

    try:
        tk = tokens[state.end_index]
    except IndexError:
        return False
    return tk.lineno == last.lineno


@check_indent(how=operator.ge, last=_undef)
def check_indent_inc(): ...


@check_indent(how=operator.le, last=_undef)
def check_indent_dec(): ...


@check_indent(how=operator.eq, last=_undef)
def check_indent_eq(): ...


def join_token_values(tks: Sequence[Tokenizer]):
    return ''.join(e.value for e in tks)


def typed_number_from_token(tk: Tokenizer):
    num = eval(tk.value)
    return Number(tk.lineno, tk.colno, num, NativeType.i64 if isinstance(num, int) else NativeType.f64)


def loc(tk: Tokenizer):
    return tk.lineno, tk.colno
