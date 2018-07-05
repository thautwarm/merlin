from typing import Dict, List, Optional
from rml.asdl import *


class _Undef:
    pass


"""
type S of 'a = 
    | F Int 'a
    | G Int S of 'b

let t  = fn F(1, x) -> x
S of 'a -> 'a
  
"""


class SymTable:
    _undef = _Undef()

    def __init__(self, parent: 'SymTable' = None):  # parent is for building closure dynamically.
        self._var_storage: List[ASDL] = []
        self._var_types: List[TypeSig] = []

        self._var_index: Dict[str, int] = {}
        self._parent = parent

    def get(self, key: str, default_factory=lambda: None):
        _undef = self._undef
        v = self._var_index.get(key, _undef)

        # if parent contains this var, append it to closure
        if self._parent:
            idx = self._parent.get_index(key)
            var = self._parent._var_storage[idx]
            self.add(key, var)
            return var

        if v is _undef:
            return default_factory()
        return self._var_storage[v]

    def get_index(self, key, default_factory=lambda: -1):
        _undef = self._undef
        v = self._var_index.get(key, _undef)

        if self._parent:
            idx = self._parent.get_index(key)
            var = self._parent._var_storage[idx]
            self.add(key, var)
            return var

        if v is -1:
            return default_factory()
        return v

    def add(self, key, var):
        idx = self._var_index.get(key, -1)
        if idx is -1:
            n = len(self._var_index)
            self._var_index[key] = n + 1
            self._var_storage.append(var)


class Context:
    def __init__(self, symtable: SymTable, closure: SymTable, glob: Optional[SymTable] = None):
        self.symtable = symtable
        self.closure = closure
        self.glob = glob
        self._subs = []

    def create_sub(self):
        pass
