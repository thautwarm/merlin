import types
from Redy.Opt.ConstExpr import optimize, const
from rml.compiler.bc import build_inst, bc


class Compiler:

    def __init__(self):
        self.consts = []
        self.var_names = []
        self.cell_vars = []
        self.names = []
        self.free_vars = []
        self.name = None
        self.codes = []
        self.lnotab = []
        self.firstlineno = None
        self.filename = None

        @optimize
        def index_const(var):
            consts: const = self.consts
            _append: const = self.consts.append
            _index: const = self.consts.index

            if var not in consts:
                _append(var)
                return len(consts) - 1

            return _index(var)

        @optimize
        def index_names(var):
            names: const = self.names
            _append: const = self.names.append
            _index: const = self.names.index

            if var not in names:
                _append(var)
                return len(names) - 1

            return _index(var)

        @optimize
        def index_var_names(var):
            names: const = self.var_names
            _append: const = self.var_names.append
            _index: const = self.var_names.index

            if var not in names:
                _append(var)
                return len(names) - 1

            return _index(var)

        self.index_consts = index_const
        self.index_names = index_names
        self.index_var_names = index_var_names

    def add_inst(self, op, arg, lineno):
        self.firstlineno = now_src_code_lineno = lineno

        _lnotab = self.lnotab
        _lnotab.append(0)
        _lnotab.append(lineno)

        now_bc_lineno = 0

        @optimize
        def _add_inst(op_, arg_, lineno_):
            nonlocal now_bc_lineno, now_src_code_lineno
            lnotab: const = _lnotab
            codes: const = self.codes

            new_codes = build_inst(op_, arg_)
            codes.extend(new_codes)

            if lineno_ > now_src_code_lineno:
                n_bc = len(codes)

                inc_of_bc = n_bc - now_bc_lineno
                inc_of_src = lineno_ - now_src_code_lineno

                now_bc_lineno, now_src_code_lineno = lineno_, n_bc

                lnotab.append(inc_of_bc)
                lnotab.append(inc_of_src)

        setattr(self, 'add_inst', _add_inst)
        _add_inst(op, arg, lineno)
