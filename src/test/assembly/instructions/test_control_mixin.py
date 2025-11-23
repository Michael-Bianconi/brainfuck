from src.test.test_assembler import TestAssembler


class TestControlMixin(TestAssembler):

    def test_call(self):

        cases = [()]

        def source(case):
            return f"""
                ALOC a 1                # >                     [0 | 0]
                FUNC addtoa             
                    PUSH @top @a        # <[->+>+<<]>>[-<<+>>]  [0 0 | 0]
                    PLUS @top @top 3    # +++><[<+>-]           [0 3 | 0]
                    POPV @a @top        # <<[-]>><[<+>-]<       [3 | 0 0]
                    RTRN                # <[->>+>+<<<]>>>[-<<<+>>>]+++><[<+>-]<<<[-]>>><[<<+>>-]
                CALL addtoa
                CALL addtoa
            """

        def check(case):
            self.assertStackContents([6], 1)

        self.run_and_check(cases, source, check)

    def test_cinz_8_top_symbol(self):

        cases = self.cases_immediate8()

        def source(case):
            return f"""
                ALOC a 1
                FUNC adda
                    PLUS @a @a 5
                    RTRN
                PUSH @top 10
                PUSH @top {case}
                CINZ @top adda
            """

        def check(case):
            self.assertStackContents([5 if case > 0 else 0, 10], 2)

        self.run_and_check(cases, source, check)

    def test_cwnz(self):

        cases = self.cases_immediate8()
        def source(case):
            return f"""
                ALOC a 1
                FUNC adda
                    PLUS @a @a 5
                    PUSH @top 1
                    SUBT @top @top @top
                    RTRN
                PUSH @top 10
                PUSH @top {case}
                CWNZ @top adda
            """

        def check(case):
            self.assertStackContents([(5 * case) % 255, 10], 2)

        self.run_and_check(cases, source, check)