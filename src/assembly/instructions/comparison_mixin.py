from src.assembly.instructions.assembler_mixin import AssemblerMixin


class ComparisonMixin(AssemblerMixin):

    def comparison_definitions(self):
        return {
            ("GRTR", ("Top", "Top", "Immediate")): self.grtr_8_top_top_immediate,

            ("EQLS", ("Top", "Top", "Top")): self.eqls_8_top_top_top,
            ("EQLS", ("Top", "Top", "Immediate")): self.eqls_8_top_top_immediate,
            ("EQLS:8:16:16", ("Top", "Top", "Top")): self.eqls_8_16_16_top_top_top,

            ("LAND", ("Top", "Top", "Top")): self.land_8_top_top_top,

            ("LOOR", ("Top", "Top", "Top")): self.loor_8_top_top_top,
        }

    def land_8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return ''.join([        # [0, 0 | 0]        [n, 0 | 0]      [0, y | 0]      [x, y | 0]
            '<<[>>+<<[-]]'      # [| 0, 0, 0]       [| 0, 0, 1]     [| 0, y, 0]     [| 0, y, 1]
            '>[>+<[-]]>',       # [0, 0 | 0]        [0, 0 | 1]      [0, 0 | 1]      [0, 0 | 2]
            '[-[<<+>>[-]]]<'    # [0 | 0, 0]        [0 | 0, 0]      [0 | 0, 0]      [1 | 0, 0]
        ])

    def loor_8_top_top_top(self, top1, top2, top3):
        self.stack_pointer -= 1
        return self.assemble(f"""       # [0, 0 | 0]        [n, 0 | 0]      [0, n | 0]      [n, m | 0]
            _RAW <[[-]<[-]+>]           # [0 | 0, 0]        [n | 0, 0]      [1 | 0, 0]      [1 | 0, 0]
            GRTR @top @top 0            # [0 | 0, 0]        [1 | 0, 0]      [1 | 0, 0]      [1 | 0, 0]
        """)

    def grtr_8_top_top_immediate(self, top1, top2, immediate):
        if immediate == 0:
            return ''.join([        # [0 | 0 0]     [n | 0 0]
                '+<[[-]+>-]>',      # [0 | 1 0]     [1 0 | 0]
                '[->]<'             # [| 0 0 0]     [| 1 0 0]
            ])
        else:
            raise NotImplementedError()

    def eqls_8_top_top_top(self, top1, top2, top3):
        return self.assemble(f"""
            SUBT @top @top @top
            _RAW +<
            _RAW [[-]>-<]>
            _RAW [<+>-]
        """)

    def eqls_8_16_16_top_top_top(self, top1, top2, top3):
        x1 = self.stack_pointer - 8
        x2 = self.stack_pointer - 7
        y1 = self.stack_pointer - 4
        y2 = self.stack_pointer - 3
        source = f"""
            PUSH @top @{x1}
            PUSH @top @{y1}
            EQLS @top @top @top
            #PUSH @top @{x2}
            #PUSH @top @{y2}
            #EQLS @top @top @top
            #LAND @top @top @top
            #_RAW <<<<[-]<[-]<<<[-]<[-]>>>>>>>>
            #_RAW [<<<<<<<<+>>>>>>>>-]<<<<<<
        """
        #self.stack_pointer -= 7
        return source

    def eqls_8_top_top_immediate(self, top1, top2, immediate):
        if immediate == 0:
            return ''.join([        # [0 | 0 0]     [n | 0 0]
                '+<[>-]>',          # [0 | 1 0]     [n 0 | 0]
                '[<+>->]<<'         # [| 1 0 0]     [| 0 0 0]
            ])
        else:
            raise NotImplementedError()