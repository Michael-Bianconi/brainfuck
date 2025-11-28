from src.assembly.instructions.arithmetic_mixin import ArithmeticMixin
from src.assembly.instructions.bitwise_mixin import BitwiseMixin
from src.assembly.instructions.comparison_mixin import ComparisonMixin
from src.assembly.instructions.control_mixin import ControlMixin
from src.assembly.instructions.internal_mixin import InternalMixin
from src.assembly.instructions.memory_mixin import MemoryMixin
from src.assembly.parser import Parser


class Assembler(InternalMixin, MemoryMixin, ArithmeticMixin, ComparisonMixin, ControlMixin, BitwiseMixin):

    def __init__(self):
        self.vtable = {}
        self.stack_pointer = 0
        self.instructions = {}
        self.defining_func = None
        self.instructions.update(self.internal_definitions())
        self.instructions.update(self.arithmetic_definitions())
        self.instructions.update(self.comparison_definitions())
        self.instructions.update(self.memory_definitions())
        self.instructions.update(self.control_definitions())
        self.instructions.update(self.bitwise_definitions())

    def assemble(self, source):
        parser = Parser()
        result = ""
        for line in source.splitlines():
            if line.strip() == '':
                continue
            parser.parse(line)
            if len(parser.lines) > 0:
                parser.__next__()
                if parser.mnemonic() == 'RTRN':
                    self.defining_func = None
                elif self.defining_func is not None:
                    self.vtable[self.defining_func] += line + '\n'
                else:
                    mnemonic = parser.mnemonic()
                    operands = [o.resolve(self.vtable) for o in parser.operands()]
                    operand_types = tuple([o.value_type for o in parser.operands()])
                    instruction = self.instructions[(mnemonic, operand_types)]
                    exe = instruction(*operands)
                    if '_' not in mnemonic:
                        print(f"{self.stack_pointer} {line.strip()} {exe}")
                    result += exe
        return result


    ###########################################################################
    # Control Flow                                                            #
    ###########################################################################

    def if_nonzero(self):
        """
        Starts an if-statement. Peeks at top value on the stack. If it is non-zero, enters
        the inner code block. If zero, skips code block. Must be paired with an end_if().

        If-statement inner code block must:
            * Have a stack-effect of 0.
            * Must not modify the top value on the stack.

        :return:
        """
        self.stack_pointer -= 1
        return ''.join([
            '<[[-]'
        ])

    def if_zero(self):
        return ''.join([
            self.logical_not(),
            self.if_nonzero()
        ])

    def else_block(self):      # [5 1 | ]
        return ''.join([        # enter else        do not enter else
            '>+<]>',            # [0 | 0]           [0 | 1]
            '[<+>-]<-',         # [|0 0]            [|1 0]
            '[[-]',
        ])

    def end_if(self):
        """
        Ends the enclosing if-statement. Pops the if-condition off the stack.
        :return:
        """
        return ''.join([
            ']',
        ])

    def while_nonzero(self, a):
        offset = self.stack_pointer - a
        return ''.join([            # c ... | 0
            self.left(offset),
            '[',
            self.right(offset)
        ])

    def end_while(self, a):
        offset = self.stack_pointer - a
        return ''.join([
            self.left(offset),
            '-]',
            self.right(offset)
        ])


    ###########################################################################
    # I/O Instructions                                                        #
    ###########################################################################

    def read(self, n):
        """
        Reads n bytes off standard input and stores in the next n bytes on the stack.
        :param n:
        :return:
        """
        self.stack_pointer += n
        return ',>' * n


