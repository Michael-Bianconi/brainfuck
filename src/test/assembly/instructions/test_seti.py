from src.test.test_assembler import TestAssembler


class TestSeti(TestAssembler):

    def test_seti_sp_sp(self):
        cases = [6, 250]

        def source(case):
            return f"""
                PUSH 257
                PUSH {case}
                SETI $sp $sp
            """

        def check(case):
            expected = [0] * self.prog_start
            expected[case], expected[case+1] = self.to16bit(257)

            self.assertDataPointerAlignsWithStackPointer(0)
            self.assertStackContents(expected)

        self.run_and_check(cases, source, check)

    def test_seti_rt_rs(self):
        cases = [100]

        def source(case):
            return f"""
                PUSH 257
                LOAD $v0 257
                LOAD $v1 {case}
                SETI $v1 $v0
            """

        def check(case):
            expected = [0] * (self.prog_start - 64) + self.to16bit(257)
            expected[case-64], expected[case-63] = self.to16bit(257)

            self.assertRegisters({"$v0": 257, "$v1": case})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents(expected)

        self.run_and_check(cases, source, check)