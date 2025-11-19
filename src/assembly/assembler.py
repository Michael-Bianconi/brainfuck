from src.assembly.instructions.arithmetic_mixin import ArithmeticMixin
from src.assembly.instructions.comparison_mixin import ComparisonMixin
from src.assembly.instructions.control_mixin import ControlMixin
from src.assembly.instructions.internal_mixin import InternalMixin
from src.assembly.instructions.memory_mixin import MemoryMixin
from src.assembly.parser import Parser


class Assembler(InternalMixin, MemoryMixin, ArithmeticMixin, ComparisonMixin, ControlMixin):

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

    def assemble(self, source):
        parser = Parser()
        result = ""
        for line in source.splitlines():
            if line.strip() == '':
                continue
            parser.parse(line).__next__()
            print(f"{self.stack_pointer} {line}")
            if parser.mnemonic() == 'RTRN':
                self.defining_func = None
            elif self.defining_func is not None:
                self.vtable[self.defining_func] += line + '\n'
            else:
                instruction = self.instructions[(parser.mnemonic(), tuple([o.value_type for o in parser.operands()]))]
                exe = instruction(*[o.resolve(self.vtable) for o in parser.operands()])
                result += exe
        return result


    def logical_not(self):
        """
        Pops the top value from the stack. If it is non-zero, pushes 0. If it is 0, pushes 1.
        :return:
        """
        return ''.join([        # [x, 0]
            self.load(0),       # [x, 0, 0]
            self.equals()       # If zero, [1, 0]. If nonzero, [0, 0]
        ])

    def equals(self, bitwidth=8):
        """
        Pops the top two values off the stack. If they are the same, pushes 1 onto the stack.
        If they are not the same, pushes 0 onto the stack.
        :return:
        """
        if bitwidth == 8:                           # [x, y] d=y
            return ''.join([                        # If x == y      | If x != y
                self.minus(bitwidth=bitwidth),      # [0, 0]         | [z, 0]     d=y
                '+<',                               # [0, 1]         | [z, 1]     d=x
                '[[-]>-<]>',                        # [0, 1]         | [0, 0]     d=y
                '[<+>-]'                            # [1, 0]         | [0, 0]     d=y
            ])
        elif bitwidth == 16:                        # [x1, x2, 0, 0, y1, y2, 0, 0 | 0, 0, 0, 0]
            x1 = self.stack_pointer - 8
            x2 = self.stack_pointer - 7
            y1 = self.stack_pointer - 4
            y2 = self.stack_pointer - 3
            source = ''.join([
                self.push(x1, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1 | 0, 0, 0]
                self.push(y1, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1, y1 | 0, 0]
                self.equals(bitwidth=8),            # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1 | 0, 0, 0]
                self.push(x2, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1, x2 | 0, 0]
                self.push(y2, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1, x2, y2 | 0]
                self.equals(bitwidth=8),            # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1, x2==y2 | 0, 0]
                self.logical_and(bitwidth=8),       # [x1, x2, 0, 0, y1, y2, 0, 0, x==y | 0, 0, 0]
                '<<<<[-]<[-]<<<[-]<[-]>>>>>>>>',    # [0, 0, 0, 0, 0, 0, 0, 0 | x==y, 0, 0, 0]
                '[<<<<<<<<+>>>>>>>>-]<<<<<<<',      # [x==y | 0]
            ])
            self.stack_pointer -= 8
            return source

    def greater_than(self, bitwidth=8):
        """
        Pops the a and b off the stack. If a > b, pushes 1 onto the stack. Otherwise
        pushes 0.

        2 3 0

        :return:
        """
        if bitwidth == 8:
            self.stack_pointer -= 1     # a < b            a > b
            return ''.join([            # a b | 0 0        a b | 0 0
                '<<'                # Move to a
                '['                 # While a is nonzero
                '  >>+<'            # Set t1 to 1 and move to b
                '  [>[-]>+<<-]'     # If b is nonzero, set t1 to 0 and move b to t2. Move to b.
                '  >>[<<+>>-]<'     # Move t2 back into b. Move to t1
                '  [>>+<<-]<'       # Move t1 to t3. Move to b
                '-<-]'              # b-- a-- Move to a
                '>[-]>[-]>[-]>'     # b=0 t1=0 t2=0 Move to t3
                '[<<<<+>>>>-]<<<'   # Move t3 into a. Move to b.
            ])

    def less_than(self, bitwidth=8):
        """
        Pops the a and b off the stack. If a > b, pushes 1 onto the stack. Otherwise
        pushes 0.

        2 3 0

        :return:
        """
        if bitwidth == 8:
            self.stack_pointer -= 1     # a < b            a > b
            return ''.join([            # a b | 0 0        a b | 0 0
                self.swap(),
                '<<'                # Move to a
                '['                 # While a is nonzero
                '  >>+<'            # Set t1 to 1 and move to b
                '  [>[-]>+<<-]'     # If b is nonzero, set t1 to 0 and move b to t2. Move to b.
                '  >>[<<+>>-]<'     # Move t2 back into b. Move to t1
                '  [>>+<<-]<'       # Move t1 to t3. Move to b
                '-<-]'              # b-- a-- Move to a
                '>[-]>[-]>[-]>'     # b=0 t1=0 t2=0 Move to t3
                '[<<<<+>>>>-]<<<'   # Move t3 into a. Move to b.
            ])


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


