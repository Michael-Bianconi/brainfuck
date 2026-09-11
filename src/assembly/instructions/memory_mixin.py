from src.assembly.instructions.assembler_mixin import AssemblerMixin


class MemoryMixin(AssemblerMixin):

    def memory_definitions(self):
        return {
            ("ALOC:16", ("Symbol", "Immediate")): self.aloc_16,

            ("GETI", ("Top", "Top")): self.geti_8_top_top,
            ("GETI:16", ("Top", "Top")): self.geti_16_top_top,

            ("PUSH", ("Top", "Top")): self.push_8_8_top_top,
            ("PUSH", ("Top", "Immediate")): self.push_8_top_immediate,
            ("PUSH", ("Top", "Address")): self.push_8_8_top_address,
            ("PUSH", ("Address", "Immediate")): self.push_8_address_immediate,
            ("PUSH:16", ("Top", "Top")): self.push_16_top_top,
            ("PUSH:16", ("Top", "Immediate")): self.push_16_top_immediate,
            ("PUSH:16", ("Top", "Address")): self.push_16_16_top_address,
            ("PUSH:16", ("Address", "Immediate")): self.push_16_address_immediate,

            ("POPV", ("Top",)): self.popv_8_top,
            ("POPV", ("Address", "Top")): self.popv_8_8_address_top,
            ("POPV:16", ("Top",)): self.popv_16_top,
            ("POPV:16", ("Address", "Top")): self.popv_16_address_top,

            ("SETI", ("Top", "Top")): self.seti_8_8_top_top,
            ("SETI:16", ("Top", "Top", "Top")): self.seti_16_top_top_top,

            ("SWAP", ("Top", "Top")): self.swap_8_8_top_top,
            ("SWAP:16", ("Top", "Top")): self.swap_16_top_top,
        }

    def aloc_16(self, symbol, immediate):
        """
        ALOC:16 (ALLOCATE 16-BIT)

        Allocates space for a variable on the stack. Stores variable name in vtable.
        Moves stack pointer to next position.

        Equivalent to a PUSH, but creates a symbol for stack position.

        :param symbol: Address label.
        :param immediate: Number of 16-bit values to push onto the stack.
        """
        self.vtable[symbol] = self.stack_pointer
        self.stack_pointer += immediate * 2
        return self.assemble(f"_MDR {immediate * 2}")

    def push_8_8_top_top(self, top1, top2):

        return self.assemble(f"PUSH @top @{self.stack_pointer - 1}")

    def push_16_top_top(self, top1, top2):
        """
        PUSH:16 @TOP @TOP

        BEHAVIOR:
            1. Pushes the top value on the stack to the top of the stack (copying it).
            2. Increments stack pointer by 2.

        EXAMPLE:
            PUSH @top @top
            [0 0 2 0 4 0] > [0 0 2 0 2 0 6 0]
        """
        return self.assemble(f"""
            _CPY:16 2 4
            _SET:16 0
            _MDL 2
            _CPY:16 2 8
            _MDR 4
            _ADD:16 2
        """)

    def push_8_top_immediate(self, top, immediate):
        self.stack_pointer += 1
        return self.assemble(f"""
             _ADD {immediate}
             _MDR 1
         """)

    def push_16_top_immediate(self, top, immediate):
        """
        PUSH @TOP IMM

        BEHAVIOR:
            1. Pushes the provided 16-bit immediate value onto the stack.
            2. Increments the stack pointer by 2.

        EXAMPLE:
            PUSH @top 5
            [0 0 2 0] > [0 0 5 0 2 0]
        """
        return self.assemble(f"""
            _MOV:16 4    
            _ADD:16 {immediate}
            _MDR:8 4
            _ADD:16 2
            _MOV:16 -2
            _MDL:8 2
        """)

    def push_8_8_top_address(self, top, address):
        offset = self.stack_pointer - address
        self.stack_pointer += 1
        return self.assemble(f"""
             _MDL {offset}
             _JFZ
                 _SUB 1
                 _MDR {offset}
                 _ADD 1
                 _MDR 1
                 _ADD 1
                 _MDL {offset + 1}
             _JBN
             _MDR {offset + 1}
             _JFZ
                 _SUB 1
                 _MDL {offset + 1}
                 _ADD 1
                 _MDR {offset + 1}
             _JBN
         """)

    def push_16_16_top_address(self, top, address):
        """
        PUSH:16 @TOP @ADDR

        Pushes the 16-bit value at the provided address to the top of
        the stack. Does not modify the data at the address.
        """
        offset = self.stack_pointer - address
        self.stack_pointer += 2
        return self.assemble(f"""
             _MDL:8 {offset}
             _CPY:16 {offset} {offset + 2}
             _MDR:8 {offset + 2}
        """)

    def push_8_address_immediate(self, address, immediate):
        offset = self.stack_pointer - address
        return self.assemble(f"""
             _MDL {offset}
             _SET 0
             _ADD {immediate}
             _MDR {offset}
         """)

    def push_16_address_immediate(self, address, immediate):
        """
        PUSH:16 @ADDR IMM

        Sets the cells at the given address to a 16-bit immediate value.
        :return:
        """
        offset = self.stack_pointer - address
        low, high = immediate % 256, immediate // 256

        return self.assemble(f"""
            _MDL:8 {offset}
            _SET:8 {low}
            _MDR:8 1
            _SET:8 {high}
            _MDR:8 {offset-1}
        """)

    def geti_8_top_top(self, top1, top2):
        """
        GETI (GET INDIRECT)

        Pops an address off the stack. Pushes the value at that address onto the stack.
        Example: [10 11 12 13 14 3 ] -> [10 11 12 13 14 13]

        Note: Address must point to a location before the top value on the stack.
              Example: [10 11 12 13 14 5]
        """
        return self.assemble(f"""
                    PUSH @top {self.stack_pointer - 2}
                    SWAP @top @top
                    SUBT @top @top @top
                    _MDL 1
                    _MOV 1
                    _MDR 1
                    _CPY 1 2
                    _MDR 1
                    _JFZ         
                        _MDL 3
                        _MOV 4
                        _MDR 2
                        _MOV -1
                        _MDR 1
                        _MOV -1
                        _MDL 1
                        _SUB 1
                    _JBN
                    _MDL 3
                    _CPY 1 3
                    _MDR 2
                    _JFZ
                        _MOV 1
                        _MDL 1
                        _MOV 1
                        _MDR 4
                        _MOV -4
                        _MDL 2
                        _SUB 1
                    _JBN
                """)

    def geti_16_top_top(self, top1, top2):
        """
        GETI:16 @TOP @TOP (GET INDIRECT)

        BEHAVIOR:
            1. Pops an absolute address off the stack. Pushes the 16-bit value at that
               location in memory onto the stack.
            2. Stack pointer remains unchanged.

        EXAMPLE:
            GETI @top @top
            [5 0 6 0 7 0 2 0 8 0] > [5 0 6 0 7 0 7 0 8 0]

        NOTES:
            1. The address MUST be a multiple of 2, and be at least 4 less than the stack pointer
               (it cannot point to the address being used for this instruction).
        """
        return self.assemble(f"""
                    _CPY:16 2 4
                    _MDR 2
                    _ADD:16 2
                    PUSH:16 @top 4
                    SUBT:16 @top @top @top
                    SWAP:16 @top @top
                    SUBT:16 @top @top @top
                    PUSH:16 @top 0
                    SWAP:16 @top @top
                    PUSH:16 @top @top
                    _MOV:16 4
                    _MDL 2
                    _JFZ
                        _MDL 6
                        _MOV:16 8
                        _MDR 4
                        _MOV:16 -2
                        _MDR 2
                        _MOV:16 -2
                        _MDL 2
                        _SUB:16 2
                    _JBN
                    _MDR 1
                    _JFZ
                        _MDL 1
                        _MDL 6
                        _MOV:16 8
                        _MDR 4
                        _MOV:16 -2
                        _MDR 2
                        _MOV:16 -2
                        _MDL 2
                        _SUB:16 2
                        _JFZ
                            _MDL 6
                            _MOV:16 8
                            _MDR 4
                            _MOV:16 -2
                            _MDR 2
                            _MOV:16 -2
                            _MDL 2
                            _SUB:16 2
                        _JBN
                        _MDR 1
                    _JBN
                    _MDL 1
                    _MDL 6
                    _CPY:16 2 6
                    _MDR 4
                    _JFZ
                        _MOV:16 2
                        _MDL 2
                        _MOV:16 2
                        _MDR 8
                        _MOV:16 -8
                        _MDL 4
                        _SUB:16 2
                    _JBN
                    
                    _MDR 1
                    _JFZ
                        _MDL 1
                        _MOV:16 2
                        _MDL 2
                        _MOV:16 2
                        _MDR 8
                        _MOV:16 -8
                        _MDL 4
                        _SUB:16 2
                        _JFZ
                            _MOV:16 2
                            _MDL 2
                            _MOV:16 2
                            _MDR 8
                            _MOV:16 -8
                            _MDL 4
                            _SUB:16 2
                        _JBN
                        _MDR 1
                    _JBN
                    _MDL 1
                    _MDR 8
                    _MOV:16 -8
                    _MDL 8
                    _SUB:16 4
                """)


    def seti_8_8_top_top(self, top1, top2):
        """
        SETI (SET INDIRECT 8-BIT)

        Pops the value to write off the stack. Pops an address off the stack.
        Sets the cell at that address to the provided value.

        1. Set up initial state [... v a|0 0] > [... v a a 0]
        """
        self.stack_pointer -= 2
        source = self.assemble(f"""
            PUSH @top {self.stack_pointer - 1}
            SWAP @top @top
            SUBT @top @top @top
            _MDL 1
            _CPY 1 2
            _MDR 1
            _JFZ
                _MDL 3
                _MOV 4
                _MDR 1
                _MOV -1
                _MDR 1
                _MOV -1
                _MDR 1
                _MOV -1
                _MDL 1
                _SUB 1
            _JBN
            _MDL 3
            _SET 0
            _MDR 1
            _MOV -1
            _MDR 1
            _JFZ
                _MOV 1
                _MDR 3
                _MOV -4
                _MDL 2
                _SUB 1
            _JBN
            _MDL 1
            """)
        return source

    def seti_16_top_top_top(self, top1, top2, top3):
        """
        SETI (SET INDIRECT 8-BIT)

        Pops the value to write off the stack. Pops an address off the stack.
        Sets the cell at that address to the provided value.

        1. Set up initial state [... v a|0 0] > [... v a a 0]
        """
        source = self.assemble(f"""
            _CPY:16 2 4
            _MDR 2
            _ADD:16 2
            PUSH:16 @top 6
            SUBT:16 @top @top @top
            SWAP:16 @top @top
            SUBT:16 @top @top @top
            PUSH:16 @top @top
            _MOV:16 2
            _MDL 2
            _DBG
            _DBG
            _JFZ
                _MDL 6
                _MOV:16 8
                _MDR 2
                _MOV:16 -2
                _MDR 2
                _MOV:16 -2
                _MDR 2
                _MOV:16 -2
                _MDL 2
                _SUB:16 2
            _JBN
            _DBG
            _DBG
            _MDR 1
            _JFZ
                _MDL 7
                _MOV:16 8
                _MDR 2
                _MOV:16 -2
                _MDR 2
                _MOV:16 -2
                _MDR 2
                _MOV:16 -2
                _MDL 2
                _SUB:16 2
                _JFZ
                    _MDL 6
                    _MOV:16 8
                    _MDR 2
                    _MOV:16 -2
                    _MDR 2
                    _MOV:16 -2
                    _MDR 2
                    _MOV:16 -2
                    _MDL 2
                    _SUB:16 2
                _JBN
                _MDR 1
            _JBN
            _DBG
            _DBG
            _MDL 7
            _SET:16 0
            _MDR 2
            _MOV:16 -2
            _MDR 2
            _JFZ
                _MOV:16 2
                _MDR 6
                _MOV:16 -8
                _MDL 4
                _SUB:16 2
            _JBN
            _MDR 1
            _JFZ
                _MDL 1
                _MOV:16 2
                _MDR 6
                _MOV:16 -8
                _MDL 4
                _SUB:16 2
                _JFZ
                    _MOV:16 2
                    _MDR 6
                    _MOV:16 -8
                    _MDL 4
                    _SUB:16 2
                _JBN
                _MDR 1
            _JBN
            _MDR 5
            _MOV:16 -8
            _MDL 8
            _SUB:16 6
            """)
        return source

    def swap_8_8_top_top(self,  top1, top2):
        """
        Pops b off the stack. Pops a off the stack. Pushes b onto the stack. Pushes a onto the stack.
        :param bitwidth:
        :return:
        """
        return ''.join([                    # [a, b | 0]
            '<[>+<-]',                      # [a | 0, b]
            '<[>+<-]>>',                    # [0, a | b]
            '[<<+>>-]'                      # [b, a | 0]
        ])

    def swap_16_top_top(self, top1, top2):
        """
        SWAP @TOP @TOP

        BEHAVIOR:
            1. Swaps the top value on the stack with the 2nd top value.
            2. Stack pointer remains unchanged.

        EXAMPLE:
            SWAP @top @top
            [0 0 4 0 3 0 6 0] > [0 0 3 0 4 0 6 0]
        """
        return self.assemble(f"""
            _MDL 2
            _MOV:16 4
            _MDL 2
            _MOV:16 2
            _MDR 6
            _MOV:16 -6
            _MDL 2
        """)

    def popv_8_top(self, top):
        self.stack_pointer -= 1
        return '<[-]'

    def popv_16_top(self, top):
        """
        POPV:16 @TOP (POP VALUE 16-BIT)

        Sets the top 16-bit value on the stack to 0 and moves the stack pointer
        to the preceding value.

        :param top: Unused
        """
        self.stack_pointer -= 2
        return '<[-]<[-]'

    def popv_8_8_address_top(self, address, top):
        offset = (self.stack_pointer - address) - 1
        source = self.assemble(f"""
            PUSH @{address} 0      # Set dest to 0
            _MDL 1              # Move data pointer to top value on the stack
            _JFZ                # While top value is nonzero
                _MDL {offset}   #   Move to dest
                _ADD 1          #   Add 1
                _MDR {offset}   #   Move to top
                _SUB 1          #   Sub 1
            _JBN                # Repeat until top is zero
        """)
        self.stack_pointer -= 1
        return source

    def popv_16_address_top(self, address, top):
        """
        POPV:16 @ADDR @TOP (POP VALUE 16-BIT)

        Pops the top value off the stack, moving it to the specified address.
        """
        offset = self.stack_pointer - address
        source = self.assemble(f"""
            _MDL:8 {offset}
            _SET:16 0
            _MDR:8 {offset-2}
            _MOV:16 {-(offset-2)}
        """)
        self.stack_pointer -= 2
        return source
