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
        }

    def divi8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return self.assemble(f"""
            _RAW <<[->[->+>>]>[<<+>>[-<+>]>+>>]<<<<<]>[>>>]>[[-<+>]>+>>]<<[<<<+>>>-]<[-]<[-]
        """)

    def divi8_top_top_immediate(self, top1, top2, immediate):
        return self.assemble(f"""
            PUSH @top {immediate}
            DIVI @top @top @top
        """)

    def plus_8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return self.assemble(f"""
            _LFT 1
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
        self.stack_pointer -= 4
        return self.assemble(f"""
            _LFT:16 1
            _RAW >[<
                _LFT:16 1
                _ADD:16 256
                _MDR:16 1
                _SUB:16 256
            _RAW >]<[
                _LFT:16 1
                _ADD:16 1
                _MDR:16 1
                _SUB:16 1
            _RAW ]
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
            _RAW <[>+<-]>>                  # [0 | a 0]
            _ADD {immediate}                # [0 a | b]
            _RAW <[>->+<[>]>[<+>-]<<[<]>-]  # [0 | a b]
            _RAW >[-]>[<<<+>>>-]>[-]<<<
        """)

    def subt_8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return '_RAW <[<->-]'

    def subt_16_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 4
        return self.assemble(f"""
            _LFT:16 1
            _RAW >[<
                _LFT:16 1
                _SUB:16 256
                _MDR:16 1
                _SUB:16 256
            _RAW >]<[
                _LFT:16 1
                _SUB:16 1
                _MDR:16 1
                _SUB:16 1
            _RAW ]
        """)
