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