from src.assembly.instructions.assembler_mixin import AssemblerMixin


class InternalMixin(AssemblerMixin):
    """
    INTERNAL INSTRUCTIONS

    Internal instructions directly manipulate the tape without regard for BFOS data
    layouts. Use with extreme caution.
    """

    def internal_definitions(self):
        return {
            ("_RAW", ("String",)): self.raw,
            ("_MDR", ("Immediate",)): self.mdr_8,
            ("_MDL", ("Immediate",)): self.mdl_8,
            ("_CPY", ("Immediate", "Immediate")): self.cpy_8,
            ("_MOV", ("Immediate",)): self.mov_8,
            ("_MMV", ("Immediate", "Immediate")): self.mmv_8,
            ("_ADD", ("Immediate",)): self.add_8,
            ("_SUB", ("Immediate",)): self.sub_8,
            ("_SET", ("Immediate",)): self.setcell_8,
            ("_JFZ", ()): self.jfiz,
            ("_JBN", ()): self.jbnz,
            ("_DBG", ()): self.dbg,
            ("_HLT", ()): self.hlt,

            ("_ADD:16", ("Immediate",)): self.add_16,
            ("_MDL:16", ("Immediate",)): self.mdl_16,
            ("_MOV:16", ("Immediate",)): self.mov_16,
            ("_CPY:16", ("Immediate", "Immediate")): self.cpy_16,
            ("_MDR:16", ("Immediate",)): self.mdr_16,
            ("_SET:16", ("Immediate",)): self.setcell_16,
            ("_SUB:16", ("Immediate",)): self.sub_16,
        }

    def mdr_8(self, immediate):
        """
        MDR:8 (MOVE DATA POINTER RIGHT 8-BIT)

        :param immediate: Moves data pointer right by immediate value.
        - If the immediate value is negative, move left.
        - If the immediate value is zero, do nothing.
        """
        return '>' * immediate if immediate >= 0 else self.mdl_8(-immediate)

    def mdr_16(self, immediate):
        """
        MDR:16 (MOVE DATA POINTER RIGHT 16-BIT)

       :param immediate: Moves data pointer right by immediate value.
        - If the immediate value is negative, move left.
        - If the immediate value is zero, do nothing.
        """
        return '>>' * immediate if immediate >= 0 else self.mdl_16(-immediate)

    def mdl_8(self, immediate):
        """
        MDL:8 (MOVE DATA POINTER LEFT 8-BIT)

        :param immediate: Moves data pointer left by immediate value.
        - If the immediate value is negative, move right.
        - If the immediate value is zero, do nothing.
        """
        return '<' * immediate if immediate >= 0 else self.mdr_8(-immediate)

    def mdl_16(self, immediate):
        """
        MDL:16 (MOVE DATA POINTER LEFT 16-BIT)

        :param immediate: Moves data pointer left by immediate value.
        - If the immediate value is negative, move right.
        - If the immediate value is zero, do nothing.
        """
        return '<<' * immediate if immediate >= 0 else self.mdr_16(-immediate)

    def mov_8(self, immediate):
        """
        MOV:8 (MOVE 8-BIT)

        Moves the value in the current cell right by the specified immediate value.
        Sets the current cell to 0. Does not change the data pointer.

        :param immediate:
        :return:
        """
        return f'[{self.mdr_8(immediate)}+{self.mdl_8(immediate)}-]'

    def mmv_8(self, imm1, imm2):
        """
        MMV:8 (MULTI-MOVE 8-BIT)

        Moves a value from the current cell into two other cells. Sets the
        current cell to 0.
        """
        return self.assemble(f"""
            _JFZ
                _SUB 1
                _MDR {imm1}
                _ADD 1
                _MDR {imm2 - imm1}
                _ADD 1
                _MDL {imm2}
            _JBN
        """)

    def mov_16(self, immediate):
        return self.assemble(f"""
            _MOV:8 {immediate}
            _MDR:8 1
            _MOV:8 {immediate}
            _MDL:8 1
        """)

    def cpy_8(self, dest, temp):
        """
        COPY:8 (COPY 8-BIT)

        Copies current 8-bit value to another location on the tape.
        Data pointer does not move.

        :param dest: The location to copy the current cell to, expressed
                     as a delta from the current data pointer (e.g. 2 means
                     2 cells to the right). Must be 0.
        :param temp: The location to use as temporary storage, expressed
                     as a delta from the current data pointer (e.g. 2 means
                     2 cells to the right). Must be 0.
        """
        return self.assemble(f"""
             _MMV {dest} {temp}
             _MDR {temp}
             _MOV {-temp}
             _MDL {temp}
         """)


    def cpy_16(self, dest, temp):
        """
        COPY:16 (COPY 16-BIT)

        Copies current 16-bit value to another location on the tape.

        :param dest: The location to copy the current cell to, expressed
                     as a delta from the current data pointer (e.g. 2 means
                     2 cells to the right). Must be 0.
        :param temp: The location to use as temporary storage, expressed
                     as a delta from the current data pointer (e.g. 2 means
                     2 cells to the right). Must be 0.
        """

        return self.assemble(f"""
            _CPY:8 {dest} {temp}
            _MDR:8 1
            _CPY:8 {dest} {temp}
            _MDL:8 1
        """)

    def jfiz(self):
        """
        _JFZ (JUMP FORWARD IF ZERO)
        """
        return "["

    def jfiz_16(self):
        """
        _JFZ (JUMP FORWARD IF ZERO 16-BIT)

        Where _JFZ:8 jumps if the current cell is 0, _JFZ:16 jumps only if
        both the current and next cells are 0.

        NOTE: _JFZ:16 must always be used in conjunction with _JBN:16
          v
        [ 0 1 ]
        """
        return ">[[...]"

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
                _MDL 1
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
                _MDL 1
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

    def dbg(self):
        """
        _DBG (DEBUG)

        Toggles debug-mode on or off.

        NOTE: This Brainfuck instruction is non-standard. It was used by the original
              creator of Brainfuck during their testing, but is not part of the
              proper Brainfuck instruction set. Some interpreters may ignore this
              instruction or assign different behavior.
        """
        return "#"

    def hlt(self):
        """
        _HLT (HALT)

        Ends the program.

        NOTE: This Brainfuck instruction is non-standard, even more so than the debug #
              instruction. While many Brainfuck extensions implement some halting
              instruction, there is no standard or even common convention for it.
              BFOS uses (H)alt. To maintain maximal compatibility with interpreters,
              this should be used only for debugging purposes.
        """
        return "H"