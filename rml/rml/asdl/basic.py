from typing import NamedTuple, Union, Tuple, TypeVar
from Redy.Magic.Classic import record, discrete_cache

from Redy.ADT.Core import data
from Redy.ADT import traits
import numpy as np

globals()['NamedTuple'] = object


class NativeType:
    i = int
    f = float
    s = str
    v = None
    b = bool
    o = object
    # python untyped object

    # i8 = np.int8
    # i16 = np.int16
    # i32 = np.int32
    # i64 = np.int64
    # ui8 = np.uint8
    # ui16 = np.uint16
    # ui32 = np.uint32
    # ui64 = np.uint64
    #
    # f16 = np.float16
    # f32 = np.float32
    # f64 = np.float64


T = TypeVar('T')


class ASDL:
    pass


@record
class Symbol(ASDL, NamedTuple):
    lineno: int
    colno: int

    value: str

    def to_name(self):
        return self.value.split('@', 1)[0]


@record
class Number(ASDL, NamedTuple):
    lineno: int
    colno: int

    num: Union[int, float]
    type: NativeType


@record
class String(ASDL, NamedTuple):
    lineno: int
    colno: int
    value: str

    def len(self):
        return len(self.value)


class Const:
    @record
    class true(ASDL, NamedTuple):
        lineno: int
        colno: int

    @record
    class false(ASDL, NamedTuple):
        lineno: int
        colno: int

    @record
    class nil(ASDL, NamedTuple):
        lineno: int
        colno: int
