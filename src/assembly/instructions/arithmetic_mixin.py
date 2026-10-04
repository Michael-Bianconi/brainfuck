from src.assembly.instructions.assembler_mixin import AssemblerMixin


class ArithmeticMixin(AssemblerMixin):

    def arithmetic_definitions(self):
        return {

            ("DIVI", ("Top", "Top", "Top")): self.divi8_top_top_top,
            ("DIVI", ("Top", "Top", "Immediate")): self.divi8_top_top_immediate,

            ("MODS", ("Top", "Top", "Immediate")): self.mods_8_top_top_immediate,

            ("MULT", ("Top", "Top", "Top")): self.mult_8_top_top_top,
            ("MULT", ("Top", "Top", "Immediate")): self.mult_8_top_top_immediate,
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




