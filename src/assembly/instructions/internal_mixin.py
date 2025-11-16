from src.assembly.instruction import Instruction
from src.assembly.parser import Immediate, Raw


class InternalMixin:

    def internal_definitions(self):
        return {
            "_RAW": Instruction(self.raw, [[Raw]]),
            "_RIT": Instruction(self.right, [[Immediate]]),
            "_LFT": Instruction(self.left, [[Immediate]]),
            "_ADD": Instruction(self.add, [[Immediate]]),
            "_SUB": Instruction(self.sub, [[Immediate]]),
            "_SET": Instruction(self.setcell, [[Immediate]]),
            "_JFZ": Instruction(self.jfiz, [[]]),
            "_JBN": Instruction(self.jbnz, [[]])
        }

    def right(self, operands, operand_types):
        """
        Moves data pointer right by immediate value.
        :param i: The immediate value to move by.
        :param bitwidth: 8-bit (1 cell) by default. May be 8, 16, 24, or 32.
        :return:
        """
        [immediate] = operands
        if immediate.bitwidth == 8:
            return '>' * immediate.value
        elif immediate.bitwidth == 16:
            return '>>>>' * immediate.value

    def left(self, operands, operand_types):
        [immediate] = operands
        if immediate.bitwidth == 8:
            return '<' * immediate.value
        elif immediate.bitwidth == 16:
            return '<<<<' * immediate.value

    def jfiz(self, operands, operand_types):
        return "["

    def jbnz(self, operands, operand_type):
        return "]"

    def add(self, operands, operand_types):
        """
        Calling this method with a large i will enable certain optimizations not available
        if a small i is used many times.

        :param i: The amount to increment the current value by.
        :param bitwidth: 8|16
        :return:
        """
        [immediate] = operands
        if immediate.bitwidth == 8:  # [x] data pointer at x
            return '+' * (immediate.value % 256)
        elif immediate.bitwidth == 16:  # [low, high, carry, temp] data pointer at x
            result = ''
            high_add = immediate.value // 256
            low_add = immediate.value % 256

            # Save potentially billions of cycles (for very large i) by modifying the high bits directly,
            # adding 256 to the total value each time. This block can be omitted entirely by repeating the +1
            # block by the full value of i.
            if high_add > 0:
                result += self.assemble(f"""
                    _RIT 1
                    _ADD {high_add}:8
                    _LFT 1
                """)

            # Add +1 to the low bits. If that causes an overflow, increment the high bits by +1.
            # Repeat this +1 process as many times as need.
            result += ''.join([  # If low+1 == 0       |   If low+1 != 0
                '+',  # [0, high, 0, 0]      |   [low+1, high, 0, 0]      d=low
                '[>>+>+<<<-]'  # [0, high, 0, 0]      |   [0, high, low+1, low+1]  d=low
                '>>[<<+>>-]+>',  # [0, high, 1, 0]      |   [low+1, high, 1, low+1]  d=temp
                '[<->[-]]<',  # [0, high, 1, 0]      |   [low+1, high, 0, 0]      d=carry
                '[-<+>]<<'  # [0, high+1, 0, 0]    |   [low+1, high, 0, 0]      d=low
            ]) * low_add

            return result

    def sub(self, operands, operand_types):
        [immediate] = operands
        if immediate.bitwidth == 8:
            return '-' * immediate.value
        elif immediate.bitwidth == 16:  # [x, y, c, t] data pointer at x
            high_sub = immediate.value // 256
            low_sub = immediate.value % 256
            result = ''
            # Save potentially billions of cycles (for very large i) by modifying the high bits directly,
            # adding 256 to the total value each time. This block can be omitted entirely by repeating the +1
            # block by the full value of i.
            if high_sub > 0:
                result += self.assemble(f"""
                _RIT 1
                _SUB {high_sub}:8
                _LFT 1
                """)
            result += ''.join([  # If x == 0         |   If x != 0           d=x
                '[>>+>+<<<-]>>',  # [0, y, x, x]      |   [x, y, 0, 0]        d=c
                '[<<+>>-]+>',  # [x, y, 1, x]      |   [x, y, x, x]        d=t
                '[<->[-]]<',  # [x, y, 0, 0]      |   [x, y, 1, 0]        d=c
                '[-<->]<<-'  # [x-1, y, 0, 0]    |   [255, y-1, 0, 0]    d=x
            ]) * low_sub
            return result

    def raw(self, operands, operand_types):
        return operands[0].value

    def setcell(self, operands, operand_types):
        [immediate] = operands
        result = ""
        if immediate.bitwidth == 8:
            result += '[-]'
        elif immediate.bitwidth == 16:
            result += '[-]>[-]<'
        result += self.assemble(f"_ADD {immediate}")
        return result