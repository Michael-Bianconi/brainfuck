import random

from src.assembly.instructions.assembler_mixin import AssemblerMixin


class ControlMixin(AssemblerMixin):

    def control_definitions(self):
        return {
            ("CALL", ("Symbol",)): self.call,
            ("CINZ", ("Top", "Symbol")): self.cinz_8_top_symbol,
            ("CINZ", ("Top",)): self.cinz8_top,
            ("FUNC", ("Symbol",)): self.func,
            ("RTRN", ()): self.rtrn,
            ("CWNZ", ("Top", "Symbol")): self.cwnz8_top_symbol
        }

    def call(self, symbol):
        return self.assemble(self.vtable[symbol])

    def cinz8_top(self, top):
        self.defining_anon = True
        return self.assemble(f"""
            FUNC anonfunc{random.randint(0,100)}
        """)

    def cinz_8_top_symbol(self, top, symbol):
        source = self.assemble(f"""
            _RAW <[>
            CALL {symbol}
            _RAW <[-]]
        """)
        self.stack_pointer -= 1
        return source

    def func(self, symbol):
        if self.defining_func is not None:
            raise RuntimeError("Cannot define function inside other function")
        elif symbol in self.vtable:
            raise KeyError("Function already defined: " + symbol)
        else:
            self.defining_func = symbol
            self.vtable[symbol] = ""
            return ""

    def rtrn(self):
        return ""

    def cwnz8_top_symbol(self, top ,symbol):
        source = self.assemble(f"""
            _RAW <[>
            CALL {symbol}
            _RAW <]
        """)
        self.stack_pointer -= 1
        return source
