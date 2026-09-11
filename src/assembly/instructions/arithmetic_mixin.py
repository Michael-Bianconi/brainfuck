from src.assembly.instructions.assembler_mixin import AssemblerMixin


class ArithmeticMixin(AssemblerMixin):

    def arithmetic_definitions(self):
        return {

            ("DIVI", ("Top", "Top", "Top")): self.divi8_top_top_top,
            ("DIVI", ("Top", "Top", "Immediate")): self.divi8_top_top_immediate,

            ("SUBT", ("Top", "Top", "Top")): self.subt_8_top_top_top,

            ("SUBT:16", ("Top", "Top", "Top")): self.subt_16_top_top_top,

            ("MODS", ("Top", "Top", "Immediate")): self.mods_8_top_top_immediate,

            ("MULT", ("Top", "Top", "Top")): self.mult_8_top_top_top,
            ("MULT", ("Top", "Top", "Immediate")): self.mult_8_top_top_immediate,

            ("PLUS", ("Top", "Top", "Top")): self.plus_8_top_top_top,
            ("PLUS", ("Top", "Immediate", "Top")): self.plus_8_top_immediate_top,
            ("PLUS", ("Top", "Address", "Top")): self.plus_8_top_address_top,
            ("PLUS", ("Top", "Top", "Immediate")): self.plus_8_top_top_immediate,
            ("PLUS", ("Top", "Top", "Address")): self.plus_8_top_top_address,
            ("PLUS", ("Address", "Address", "Immediate")): self.plus_8_address_address_immediate,

            ("PLUS:16", ("Top", "Top", "Top")): self.plus_16_top_top_top,
            ("PLUS:16", ("Top", "Top", "Immediate")): self.plus_16_top_top_immediate,
        }

    def divi8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return self.assemble(f"""
            _RAW "<<[->[->+>>]>[<<+>>[-<+>]>+>>]<<<<<]>[>>>]>[[-<+>]>+>>]<<[<<<+>>>-]<[-]<[-]"      
        """)

    def divi8_top_top_immediate(self, top1, top2, immediate):
        return self.assemble(f"""
            PUSH @top {immediate}
            DIVI @top @top @top
        """)

    def plus_8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return self.assemble(f"""
            _MDL 1
            _MOV -1
        """)

    def plus_8_top_immediate_top(self, top1, immediate, top2):
        return self.assemble(f"""
                PUSH @top {immediate}
                PLUS @top @top @top
        """)

    def plus_8_top_address_top(self, top1, address, top2):
        return self.assemble(f"""
                PUSH @top @{address}
                PLUS @top @top @top
        """)

    def plus_8_top_top_immediate(self, top1, top2, immediate):
        return self.assemble(f"""
                PUSH @top {immediate}
                PLUS @top @top @top
        """)

    def plus_8_top_top_address(self, top1, top2, address):
        return self.assemble(f"""
                PUSH @top @{address}
                PLUS @top @top @top
        """)

    def plus_16_top_top_top(self, top1, top2, top3):
        """
        PLUS:16 @TOP @TOP @TOP

        BEHAVIOR:
            1. Pops the top two 16-bit values off the stack, adds them together,
               and places the sum back on the stack.
            2. Decrements stack pointer by 2.

        EXAMPLE:
            PLUS @top @top @top
            [0 0 5 0 3 0 6 0] > [0 0 8 0 4 0]
        """
        return self.assemble(f"""
            _MOV:16 4
            _MDL 2
            _MOV:16 2
            _MDR 3
            _JFZ
                _MDL 5
                _ADD:16 256
                _MDR 4
                _SUB:16 256
                _MDR 1
            _JBN
            _MDL 1
            _JFZ      
                _MDL:8 4
                _ADD:16 1
                _MDR:8 4
                _SUB:16 1
            _JBN
            _MDR 4
            _SUB:16 2
            _MOV:16 -6
            _MDL 6
        """)

    def plus_16_top_top_immediate(self, top1, top2, immediate):
        """
        PLUS:16 @TOP @TOP IMM

        BEHAVIOR:
            1. Adds an immediate value to the value at the top of the stack.
            2. Stack pointer remains unchanged.

        EXAMPLE:
            PLUS @top @top 3
            [0 0 5 0 4 0] > [0 0 8 0 4 0]
        """
        return self.assemble(f"""
            PUSH:16 @top {immediate}
            PLUS:16 @top @top @top
        """)

    def plus_8_address_address_immediate(self, address1, address2, immediate):
        return self.assemble(f"""
            PUSH @top @{address2}
            PUSH @top {immediate}
            PLUS @top @top @top
            POPV @{address1} @top
        """)

    def mult_8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return ''.join([  # [a b | 0 0]   [a 0 | 0 0]     [0 b | 0 0]     [0 0 | 0 0]
            '<<[>>>+<<<-]>>>',  # [0 b 0 | a]   [0 0 0 | a]     [0 b 0 | 0]     [0 0 0 | 0]
            '[<<[<+>>+<-]',  # [b | 0 b a]
            '>[<+>-]>',  # [b b 0 | a]
            '-]',  # [c b 0 | 0]
            '<<[-]'
        ])

    def mult_8_top_top_immediate(self, top1, top2, immediate):
        return self.assemble(f"""
            PUSH @top {immediate}
            MULT @top @top @top
        """)

    def mods_8_top_top_immediate(self, top1, top2, immediate):
        return self.assemble(f"""
            _RAW "<[>+<-]>>"                    # [0 | a 0]
            _ADD {immediate}                    # [0 a | b]
            _RAW "<[>->+<[>]>[<+>-]<<[<]>-]"    # [0 | a b]
            _RAW ">[-]>[<<<+>>>-]>[-]<<<"       
        """)

    def subt_8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return '<[<->-]'

    def subt_8_top_imm_top(self, top1, imm, top2):
        """
        SUBT:8 @TOP IMM @TOP (SUBTRACT 8-BIT)

        Pop the top value off the stack. Subtract it from the immediate value.
        Push the result onto the stack.
        """
        return self.assemble(f"""
            PUSH @top {imm}
            SWAP @top @top
            SUBT @top @top @top
        """)

    def subt_16_top_top_top(self, top1, top2, top3):
        """
        SUBT @TOP @TOP @TOP (SUBTRACT 16-BIT)

        BEHAVIOR:
            1. Pops the top two values off the stack. Subtracts the top value from
               the 2nd value on the stack. Pushes the result onto the stack.
            2. Decrements the stack pointer by 2.

        EXAMPLE:
            [0 0 5 0 3 0 6 0] > [0 0 2 0 4 0]
        """
        return self.assemble(f"""
            _MOV:16 4
            _MDL 2
            _MOV:16 2
            _MDR 3
            _JFZ
                _MDL 5
                _SUB:16 256
                _MDR 4
                _SUB:16 256
                _MDR 1
            _JBN
            _MDL 1
            _JFZ      
                _MDL:8 4
                _SUB:16 1
                _MDR:8 4
                _SUB:16 1
            _JBN
            _MDR 4
            _SUB:16 2
            _MOV:16 -6
            _MDL 6    
        """)


