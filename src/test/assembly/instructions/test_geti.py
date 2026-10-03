from src.test.test_assembler import TestAssembler


class TestGeti(TestAssembler):

    def test_geti_sp_sp(self):
        cases = [2, 250]

        def source(case):
            return f"""
                LOAD $v0 {case}
                PUSH 4
                GETI $sp $sp
            """

        def check(case):
            expected = [0, 0, 0, 0] + self.to16bit(case)

            self.assertRegisters({"$v0": case})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents(expected)

        self.run_and_check(cases, source, check)

    def test_geti_sp_register(self):
        cases = [2, 250]

        def source(case):
            return f"""
                LOAD $v0 {case}
                GETI $sp $v0
            """

        def check(case):
            expected = [0, 0, 0, 0] + self.to16bit(case)

            self.assertRegisters({"$v0": case})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents(expected)

        self.run_and_check(cases, source, check)