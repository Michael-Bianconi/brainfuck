from src.assembly.instructions.assembler_mixin import AssemblerMixin


class ControlMixin(AssemblerMixin):

    def control_definitions(self):
        return {
            ("CALL", ("Symbol",)): self.call,
            ("FUNC", ("Symbol",)): self.func,
            ("RTRN", ()): self.rtrn,
        }

    def call(self, symbol):
        print(self.stack_pointer)
        return self.assemble(self.vtable[symbol])

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
