from src.assembly.instructions.assembler_mixin import AssemblerMixin


class BitwiseMixin(AssemblerMixin):

    def bitwise_definitions(self):
        return {
            ('BAND', ('Top', "Top", "Top")): self.band8_top_top_top,

            ('BIOR', ('Top', "Top", "Top")): self.bior8_top_top_top,

            ("LSFT", ("Top", "Top", "Immediate")): self.lsft8_top_top_immediate,

            ("RSFT", ("Top", "Top", "Immediate")): self.rsft8_top_top_immediate,
        }

    def band8_top_top_top(self, top1, top2, top3):
        a = self.stack_pointer - 2
        b = self.stack_pointer - 1
        return self.assemble(f"""           # [a b | 0]
        
            PUSH @top @{a}                  # [a b a | 0]
            MODS @top @top 2                # [a b a1 | 0]
            PUSH @top @{b}                  # [a b a1 b | 0]
            MODS @top @top 2                # [a b a1 b1 | 0]
            LAND @top @top @top             # [a b c | 0]
            
            PUSH @top @{a}
            RSFT @top @top 1
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 1
            MODS @top @top 2                # [a b c a2 b2 | 0]
            LAND @top @top @top
            LSFT @top @top 1                # [a b c c2 | 0]
            PLUS @top @top @top
            
            PUSH @top @{a}
            RSFT @top @top 2
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 2
            MODS @top @top 2
            LAND @top @top @top
            LSFT @top @top 2                # [a b c c3 | 0]
            PLUS @top @top @top
                
            PUSH @top @{a}
            RSFT @top @top 3
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 3
            MODS @top @top 2
            LAND @top @top @top
            LSFT @top @top 3                # [a b c c4 | 0]
            PLUS @top @top @top
            
            PUSH @top @{a}
            RSFT @top @top 4
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 4
            MODS @top @top 2
            LAND @top @top @top
            LSFT @top @top 4                # [a b c c5 | 0]
            PLUS @top @top @top
            
            PUSH @top @{a}
            RSFT @top @top 5
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 5
            MODS @top @top 2
            LAND @top @top @top
            LSFT @top @top 5                 # [a b c c6 | 0]
            PLUS @top @top @top
            
            PUSH @top @{a}
            RSFT @top @top 6
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 6
            MODS @top @top 2
            LAND @top @top @top
            LSFT @top @top 6                 # [a b c c7 | 0]
            PLUS @top @top @top
            
            PUSH @top @{a}
            RSFT @top @top 7
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 7
            MODS @top @top 2
            LAND @top @top @top
            LSFT @top @top 7                # [a b c c8 | 0]
            PLUS @top @top @top             # [a b c | 0]
            
            SWAP @top @top
            POPV @top                       # [a c | 0]
            SWAP @top @top
            POPV @top                       # [c | 0]
        """)

    def bior8_top_top_top(self, top1, top2, top3):
        a = self.stack_pointer - 2
        b = self.stack_pointer - 1
        return self.assemble(f"""           # [a b | 0]

            PUSH @top @{a}                  # [a b a | 0]
            MODS @top @top 2                # [a b a1 | 0]
            PUSH @top @{b}                  # [a b a1 b | 0]
            MODS @top @top 2                # [a b a1 b1 | 0]
            LOOR @top @top @top             # [a b c | 0]

            PUSH @top @{a}
            RSFT @top @top 1
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 1
            MODS @top @top 2                # [a b c a2 b2 | 0]
            LOOR @top @top @top
            LSFT @top @top 1                # [a b c c2 | 0]
            PLUS @top @top @top

            PUSH @top @{a}
            RSFT @top @top 2
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 2
            MODS @top @top 2
            LOOR @top @top @top
            LSFT @top @top 2                # [a b c c3 | 0]
            PLUS @top @top @top

            PUSH @top @{a}
            RSFT @top @top 3
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 3
            MODS @top @top 2
            LOOR @top @top @top
            LSFT @top @top 3                # [a b c c4 | 0]
            PLUS @top @top @top

            PUSH @top @{a}
            RSFT @top @top 4
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 4
            MODS @top @top 2
            LOOR @top @top @top
            LSFT @top @top 4                # [a b c c5 | 0]
            PLUS @top @top @top

            PUSH @top @{a}
            RSFT @top @top 5
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 5
            MODS @top @top 2
            LOOR @top @top @top
            LSFT @top @top 5                 # [a b c c6 | 0]
            PLUS @top @top @top

            PUSH @top @{a}
            RSFT @top @top 6
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 6
            MODS @top @top 2
            LOOR @top @top @top
            LSFT @top @top 6                 # [a b c c7 | 0]
            PLUS @top @top @top

            PUSH @top @{a}
            RSFT @top @top 7
            MODS @top @top 2
            PUSH @top @{b}
            RSFT @top @top 7
            MODS @top @top 2
            LOOR @top @top @top
            LSFT @top @top 7                # [a b c c8 | 0]
            PLUS @top @top @top             # [a b c | 0]

            SWAP @top @top
            POPV @top                       # [a c | 0]
            SWAP @top @top
            POPV @top                       # [c | 0]
        """)

    def rsft8_top_top_immediate(self, top1, top2, immediate):
        if immediate >= 8:
            return self.assemble("_RAW <[-]>")
        return self.assemble(f"DIVI @top @top {(2 ** immediate) % 256}")

    def lsft8_top_top_immediate(self, top1, top2, immediate):
        return self.assemble(f"MULT @top @top {2 ** immediate}")