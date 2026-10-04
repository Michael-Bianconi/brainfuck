from src.test.test_assembler import TestAssembler


class TestSfiz(TestAssembler):

    def test_sfiz_rt(self):
        cases = [0, 10, 255, 256, 257, 65535]

        def source(case):
            return f"""
                LOAD $v1 {case}
                PUSH 10
                SIFZ $v1
                PUSH 5
                ZFIS $c0
            """

        def check(case):
            self.assertRegisters({"$v1": case})
            self.assertDataPointerAlignsWithStackPointer(2 if case == 0 else 4)
            self.assertStackContents([0, 0, 10, 0] + [] if case == 0 else [5, 0])

        self.run_and_check(cases, source, check)



