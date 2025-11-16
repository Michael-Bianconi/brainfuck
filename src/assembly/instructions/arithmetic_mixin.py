from src.assembly.instruction import Instruction
from src.assembly.parser import Address, Immediate, Top


class ArithmeticMixin:

    def arithmetic_definitions(self):
        return {
            "SUBT": Instruction(self.subtract, [
                [Top, Top, Top]
            ]),
            "MULT": Instruction(self.multiply, [
                [Top, Top, Top]
            ]),
            "PLUS": Instruction(self.plus, [
                [Top, Top, Top]])
        }

    def plus(self, operands, operand_types):
        """
        Input:  [... a b | 0]
        Output: [... a+b | 0 0]

        Pops b off the stack. Pops a off the stack. Pushes the sum of a+b to the stack.

        :param a_bits: 8|16 The size of the a value.
        :param b_bits: 8|16 The size of the b value.
        :param out_bits: 8|16 The size of the sum value.
        :return:
        """
        dest, left, right = operands
        if operand_types == [Top, Top, Top] and dest.bitwidth == 8 and left.bitwidth == 8 and right.bitwidth == 8:
            self.stack_pointer -= 1
            return '<[<+>-]'
        elif operand_types == [Top, Top, Top] and dest.bitwidth == 16 and left.bitwidth == 16 and right.bitwidth == 16:
            self.stack_pointer -= 4
            return self.assemble(f"""
                _LFT 1:16
                _RAW >[<
                    _LFT 1:16
                    _ADD 256:16
                    _RIT 1:16
                    _SUB 256:16
                _RAW >]<[
                    _LFT 1:16
                    _ADD 1:16
                    _RIT 1:16
                    _SUB 1:16
                _RAW ]
            """)

    def multiply(self, operands, operand_types):
        """
        Pops a and b off the stack. Pushes c = a * b onto the stack.
        :param bitwidth:
        :return:
        """
        dest, left, right = operands
        if operand_types == [Top, Top, Top] and dest.bitwidth == 8 and left.bitwidth == 8 and right.bitwidth == 8:
            self.stack_pointer -= 1
            return ''.join([                    # [a b | 0 0]   [a 0 | 0 0]     [0 b | 0 0]     [0 0 | 0 0]
                '<<[>>>+<<<-]>>>',              # [0 b 0 | a]   [0 0 0 | a]     [0 b 0 | 0]     [0 0 0 | 0]
                '[<<[<+>>+<-]',                 # [b | 0 b a]
                '>[<+>-]>',                     # [b b 0 | a]
                '-]',                           # [c b 0 | 0]
                '<<[-]'
            ])
        else:
            raise NotImplementedError()

    def subtract(self, operands, operand_types):
        dest, left, right = operands
        if operand_types == [Top, Top, Top] and dest.bitwidth == 8 and left.bitwidth == 8 and right.bitwidth == 8:
            self.stack_pointer -= 1
            return '<[<->-]'
        elif operand_types == [Top, Top, Top] and dest.bitwidth == 16 and left.bitwidth == 16 and right.bitwidth == 16:
            self.stack_pointer -= 4
            return self.assemble(f"""
                _LFT 1:16
                _RAW >[<
                    _LFT 1:16
                    _SUB 256:16
                    _RIT 1:16
                    _SUB 256:16
                _RAW >]<[
                    _LFT 1:16
                    _SUB 1:16
                    _RIT 1:16
                    _SUB 1:16
                _RAW ]
            """)