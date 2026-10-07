from src.assembly.instructions.assembler_mixin import AssemblerMixin


class InternalMixin(AssemblerMixin):
    """
    INTERNAL INSTRUCTIONS

    Internal instructions directly manipulate the tape without regard for BFOS data
    layouts. Use with extreme caution.
    """

    def internal_definitions(self):
        return {
            ("_RAW", ("native",)): self.raw,
            ("_MDP", ("immediate",)): self.mdp,
            ("_CPY", ("immediate", "immediate")): self.cpy_8,
            ("_MOV", ("immediate",)): self.mov_8,
            ("_MMV", ("immediate", "immediate")): self.mmv_8,
            ("_ADD", ("immediate",)): self.add_8,
            ("_SUB", ("immediate",)): self.sub_8,
            ("_SET", ("immediate",)): self.setcell_8,
            ("_EQL", ("immediate", "immediate")): self.eql_8,
            ("_NEQ", ("immediate", "immediate")): self.neq_8,
            ("_AND", ("immediate", "immediate")): self.and_8,
            ("_LOR", ("immediate", "immediate")): self.lor_8,
            ("_SOA", ("immediate",)): self.soa,
            ("_JFZ", ()): self.jfz,
            ("_JBN", ()): self.jbn,
            ("_DBG", ()): self.dbg,
            ("_HLT", ()): self.hlt,

            ("_ADD:16", ("immediate",)): self.add_16,
            ("_MOV:16", ("immediate",)): self.mov_16,
            ("_CPY:16", ("immediate", "immediate")): self.cpy_16,
            ("_SET:16", ("immediate",)): self.setcell_16,
            ("_SUB:16", ("immediate", "immediate", "immediate")): self.sub_16,
            ("_EQL:16", ("immediate", "immediate")): self.eql_16,
            ("_NEQ:16", ("immediate", "immediate")): self.neq_16,
        }

    def mdp(self, immediate):
        """
        MDP (MOVE DATA POINTER)

        :param immediate: Moves data pointer right by immediate value.
        - If the immediate value is negative, move left.
        - If the immediate value is zero, do nothing.
        """
        return '>' * immediate if immediate >= 0 else '<' * -immediate

    def mov_8(self, immediate):
        """
        MOV:8 (MOVE 8-BIT)

        Moves the value in the current cell right by the specified immediate value.
        Sets the current cell to 0. Does not change the data pointer.

        :param immediate:
        :return:
        """
        return f'[{self.mdp(immediate)}+{self.mdp(-immediate)}-]'

    def mmv_8(self, imm1, imm2):
        """
        MMV:8 (MULTI-MOVE 8-BIT)

        Moves a value from the current cell into two other cells. Sets the
        current cell to 0.
        """
        return self.assemble(f"""
            _JFZ
                _SUB 1
                _MDP {imm1 - 0}
                _ADD 1
                _MDP {imm2 - imm1}
                _ADD 1
                _MDP {0 - imm2}
            _JBN
        """)

    def mov_16(self, immediate):
        return self.assemble(f"""
            _MOV {immediate}
            _MDP 1
            _MOV {immediate}
            _MDP -1
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
                     2 cells to the right). Will be set to 0.
        """
        return self.assemble(f"""
             _MDP {temp}
             _SET 0
             _MDP {-temp}
             _MMV {dest} {temp}
             _MDP {temp}
             _MOV {-temp}
             _MDP {-temp}
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
            _CPY {dest} {temp}
            _MDP 1
            _CPY {dest} {temp}
            _MDP -1
        """)

    def jfz(self):
        """
        _JFZ (JUMP FORWARD IF ZERO)
        """
        return "["

    def jbn(self):
        return "]"

    def add_8(self, immediate):
        """
        Calling this method with a large i will enable certain optimizations not available
        if a small i is used many times.

        :param immediate:
        :return:
        """
        return '+' * (immediate % 256)

    def add_16(self, immediate):
        """
        Calling this method with a large i will enable certain optimizations not available
        if a small i is used many times.

        :param immediate:
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
                _MDP 1
                _ADD {high_add}
                _MDP -1
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

    def sub_16(self, immediate, carry, temp):
        high_sub = immediate // 256
        low_sub = immediate % 256
        x = 0
        y = 1
        result = ''
        # Save potentially billions of cycles (for very large i) by modifying the high bits directly,
        # adding 256 to the total value each time. This block can be omitted entirely by repeating the +1
        # block by the full value of i.
        if high_sub > 0:
            result += self.assemble(f"""
                _MDP 1
                _SUB {high_sub}
                _MDP -1
            """)

        result += self.assemble(f"""
            _CPY {temp} {carry}         # temp = x
            _MDP {carry}                # carry = 1
            _ADD 1
            _MDP {temp - carry}
            _JFZ                        # if temp > 0: carry = 0
                _MDP {carry - temp}
                _SUB 1
                _MDP {temp - carry}
                _SET 0
            _JBN
            _MDP {carry - temp}
            _JFZ                        # y = y - carry
                _SUB 1
                _MDP {y - carry}
                _SUB 1
                _MDP {carry - y}
            _JBN
            _MDP {x - carry}
            _SUB 1                      # x = x - 1
        """ * low_sub)
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

    def eql_8(self, imm, tmp):
        """
        _EQL imm temp (EQUALS immediate 8-BIT)
        
        BEHAVIOR:

            1. Checks if the current cell is equal to the provided immediate value.
               Sets cell to 1 if equal, 0 otherwise.
            2. Data pointer remains unchanged.

        EXAMPLE:

                        [05< 00]
            _EQI 5 1    [01< 00]

        PERFORMANCE (with an optimizing interpreter):

            Memory Complexity: 2 cells
            Time Complexity: O(1)

        NOTES:

            1. temp is the relative address of a cell used for temporary storage. This
               cell must start at 0, and will be 0 at the end.

        """
        imm = imm % 256
        return self.assemble(f"""
            _SUB {imm}
            _MDP {tmp}
            _ADD 1
            _MDP {-tmp}
            _JFZ
                _MDP {tmp}
                _SUB 1
                _MDP {-tmp}
                _SET 0
            _JBN
            _MDP {tmp}
            _MOV {-tmp}
            _MDP {-tmp}
        """)

    def and_8(self, imm, tmp):
        """
        AND IMM TMP (LOGICAL AND 8-BIT)

        BEHAVIOR:
            1. Checks if the current cell and the cell $imm cells away
               are both non-zero.
            2. If both are non-zero, sets current cell to 1. If either are
               zero, sets current cell to 0. Sets cell $imm cells away to 0.

        PERFORMANCE:
            Memory complexity: 3 cells
            Time complexity: O(1)
        """
        return self.assemble(f"""
            _JFZ
                _MDP {imm}
                _JFZ
                    _MDP {tmp - imm}
                    _ADD 1
                    _MDP {imm - tmp}
                    _SET 0
                _JBN
                _MDP {-imm}
                _SET 0
            _JBN
            _MDP {imm}
            _SET 0
            _MDP {tmp - imm}
            _MOV {-tmp}
            _MDP {-tmp}
        """)

    def lor_8(self, imm, tmp):
        """
        LOR IMM TMP (LOGICAL OR 8-BIT)

        BEHAVIOR:
            1. Checks if the current cell or the cell $imm cells away
               are non-zero.
            2. If either are non-zero, sets current cell to 1. If both are
               zero, sets current cell to 0. Sets cell $imm cells away to 0.

        EXAMPLE:
            [x, y, t]
            if x > 0

        PERFORMANCE:
            Memory complexity: 3 cells
            Time complexity: O(1)
        """
        return self.assemble(f"""
            _JFZ
                _SET 0
                _MDP {imm}
                _SET 0
                _MDP {tmp - imm}
                _ADD 1
                _MDP {-tmp}
            _JBN
            _MDP {imm}
            _JFZ
                _SET 0
                _MDP {tmp - imm}
                _ADD 1
                _MDP {imm - tmp}
            _JBN
            _MDP {tmp - imm}
            _MOV {-tmp}
            _MDP {-tmp}
        """)

    def eql_16(self, imm, tmp):
        """

        :param imm:
        :param tmp:
        :return:
        """
        lo = (imm % 65536) & 0b0000000011111111
        hi = ((imm % 65536) & 0b1111111100000000) >> 8
        return self.assemble(f"""
            _EQL {lo} {tmp}
            _MDP 1
            _EQL {hi} {tmp}
            _MOV -1
            _MDP -1
            _EQL 2 {tmp}
        """)

    def neq_8(self, imm, tmp):
        """
        _NEQ IMM TMP (NOT EQUAL TO immediate)

        BEHAVIOR:
            1. Sets current cell to 1 if value does not equal immediate.
            2. Data pointer remains unchanged.

        PERFORMANCE (with optimizing interpreter):
            Memory complexity: 2 cells
            Time complexity: O(1)
        """
        imm = imm % 256
        return self.assemble(f"""
            _SUB {imm}
            _JFZ
                _MDP {tmp}
                _ADD 1
                _MDP {-tmp}
                _SET 0
            _JBN
            _MDP {tmp}
            _MOV {-tmp}
            _MDP {-tmp}
        """)

    def neq_16(self, imm, tmp):
        """
        NEQ:16 (NOT EQUAL 16-BIT)

        :param imm:
        :param tmp:
        :return:
        """
        lo = (imm % 65536) & 0b0000000011111111
        hi = ((imm % 65536) & 0b1111111100000000) >> 8
        return self.assemble(f"""
            _NEQ {lo} {tmp}
            _MDP 1
            _NEQ {hi} {tmp-1}
            _MOV -1
            _MDP -1
            _LOR 1 {tmp}
        """)

    def soa(self, imm):
        return (".>" * imm) + ("<" * imm)
