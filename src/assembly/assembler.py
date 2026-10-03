from src.assembly.instructions.arithmetic_mixin import ArithmeticMixin
from src.assembly.instructions.bitwise_mixin import BitwiseMixin
from src.assembly.instructions.comparison_mixin import ComparisonMixin
from src.assembly.instructions.control_mixin import ControlMixin
from src.assembly.instructions.internal_mixin import InternalMixin
from src.assembly.instructions.seti import Seti
from src.assembly.instructions.geti import Geti
from src.assembly.instructions.push import Push
from src.assembly.instructions.subt import Subt
from src.assembly.instructions.swap import Swap
from src.assembly.instructions.load import Load
from src.assembly.instructions.popv import Popv
from src.assembly.parser import Parser


class Assembler(InternalMixin, Popv, Seti, Load, ArithmeticMixin, ComparisonMixin, ControlMixin, BitwiseMixin, Geti, Push, Subt, Swap):

    def __init__(self):
        self.vtable = {}
        self.next_allocation = 0
        self.stack_pointer = 0
        self.instructions = {}
        self.defining_func = None
        self.instructions.update(self.internal_definitions())
        self.instructions.update(self.arithmetic_definitions())
        self.instructions.update(self.comparison_definitions())
        self.instructions.update(self.seti_definitions())
        self.instructions.update(self.control_definitions())
        self.instructions.update(self.bitwise_definitions())
        self.instructions.update(self.geti_definitions())
        self.instructions.update(self.push_definitions())
        self.instructions.update(self.subt_definitions())
        self.instructions.update(self.swap_definitions())
        self.instructions.update(self.load_definitions())
        self.instructions.update(self.popv_definitions())

    def assemble(self, source):
        parser = Parser()
        result = ""
        for line in source.splitlines():
            if line.strip() == '':
                continue
            parser.parse(line)
            if len(parser.lines) > 0:
                parser.__next__()
                mnemonic = parser.mnemonic()
                operand_values = tuple([o.operand_value for o in parser.operands()])
                operand_types = tuple([o.operand_type for o in parser.operands()])
                instruction = self.instructions[(mnemonic, operand_types)]
                exe = instruction(*operand_values)
                if '_' not in mnemonic:
                    print(f"{self.stack_pointer} {line.strip()} {exe}")
                result += exe
        return result

    def allocate(self, symbol, size):
        self.vtable[symbol] = self.next_allocation
        self.next_allocation += size

    def init_vm(self, register_count, text_size):
        source = ""
        source += ">>" * register_count     # Space for registers
        source += ">" * text_size           # Space for .bfm file
        source += ">>"                      # Program counter

        stack_low_bits = len(source) % 256
        stack_high_bits = len(source) // 256

        source += "+" * stack_low_bits
        source += ">"
        source += "+" * stack_high_bits
        source += "<"
        return source

