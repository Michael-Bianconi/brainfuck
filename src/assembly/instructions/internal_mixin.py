from src.assembly.instructions.assembler_mixin import AssemblerMixin


class InternalMixin(AssemblerMixin):

    def internal_definitions(self):
        return {
            ("_RAW", ("Raw",)): self.raw,
            ("_MDR", ("Immediate",)): self.rit_8,
            ("_LFT", ("Immediate",)): self.lft_8,
            ("_MOV", ("Immediate",)): self.mov_8,
            ("_ADD", ("Immediate",)): self.add_8,
            ("_SUB", ("Immediate",)): self.sub_8,
            ("_SET", ("Immediate",)): self.setcell_8,
            ("_JFZ", ()): self.jfiz,
            ("_JBN", ()): self.jbnz,

            ("_ADD:16", ("Immediate",)): self.add_16,
            ("_LFT:16", ("Immediate",)): self.lft_16,
            ("_MOV:16", ("Immediate",)): self.mov_16,
            ("_MDR:16", ("Immediate",)): self.rit_16,
            ("_SET:16", ("Immediate",)): self.setcell_16,
            ("_SUB:16", ("Immediate",)): self.sub_16,
        }

    def rit_8(self, immediate):
        """
        Moves data pointer right by immediate value.
        :param i: The immediate value to move by.
        :return:
        """
        return '>' * immediate if immediate >= 0 else self.lft_8(-immediate)

    def rit_16(self, immediate):
        """
        Moves data pointer right by immediate value.
        :param i: The immediate value to move by.
        :param bitwidth: 8-bit (1 cell) by default. May be 8, 16, 24, or 32.
        :return:
        """
        return '>>>>' * immediate

    def lft_8(self, immediate):
        return '<' * immediate if immediate >= 0 else self.rit_8(-immediate)

    def mov_8(self, immediate):
        return f'[{self.rit_8(immediate)}+{self.lft_8(immediate)}-]'

    def mov_16(self, immediate):
        return f"""
            _JFZ
                _MDR:16 {immediate}
                _ADD:16 1
                _LFT:16 {immediate}
                _SUB:16 1
            _JBN
        """

    def lft_16(self, immediate):
        return '<<<<' * immediate

    def jfiz(self):
        return "["

    def jbnz(self):
        return "]"

    def add_8(self, immediate):
        """
        Calling this method with a large i will enable certain optimizations not available
        if a small i is used many times.

        :param i: The amount to increment the current value by.
        :param bitwidth: 8|16
        :return:
        """
        return '+' * (immediate % 256)

    def add_16(self, immediate):
        """
        Calling this method with a large i will enable certain optimizations not available
        if a small i is used many times.

        :param i: The amount to increment the current value by.
        :param bitwidth: 8|16
        :return:
        """
        result = ''
        high_add = immediate // 256
        low_add = immediate % 256

        # Save potentially billions of cycles (for very large i) by modifying the high bits directly,
        # adding 256 to the total value each time. This block can be omitted entirely by repeating the +1
        # block by the full value of i.
        if high_add > 0:
            result += self.assemble(f"""
                _MDR 1
                _ADD {high_add}
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

    def sub_8(self, immediate):
        return '-' * (immediate % 256)

    def sub_16(self, immediate):
        high_sub = immediate // 256
        low_sub = immediate % 256
        result = ''
        # Save potentially billions of cycles (for very large i) by modifying the high bits directly,
        # adding 256 to the total value each time. This block can be omitted entirely by repeating the +1
        # block by the full value of i.
        if high_sub > 0:
            result += self.assemble(f"""
                _MDR 1
                _SUB {high_sub}
                _LFT 1
            """)
        result += ''.join([  # If x == 0         |   If x != 0           d=x
            '[>>+>+<<<-]>>',  # [0, y, x, x]      |   [x, y, 0, 0]        d=c
            '[<<+>>-]+>',  # [x, y, 1, x]      |   [x, y, x, x]        d=t
            '[<->[-]]<',  # [x, y, 0, 0]      |   [x, y, 1, 0]        d=c
            '[-<->]<<-'  # [x-1, y, 0, 0]    |   [255, y-1, 0, 0]    d=x
        ]) * low_sub
        return result

    def raw(self, value):
        return value

    def setcell_8(self, immediate):
        return '[-]' + self.assemble(f"_ADD {immediate}")

    def setcell_16(self, immediate):
        return '[-]>[-]<' + self.assemble(f"_ADD:16 {immediate}")
