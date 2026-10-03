from src.test.test_assembler import TestAssembler


class TestLoad(TestAssembler):

    def test_load_rt_imm(self):
        cases = [10, 290]

        def source(case):
            return f"""
                PUSH 10
                LOAD $v0 {case}
                LOAD $v1 {case+1}
            """

        def check(case):
            self.assertRegisters({"$v0": case, "$v1": case+1})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([0, 0, 0, 0, 10, 0])

        self.run_and_check(cases, source, check)

    def test_load_rt_rs(self):
        cases = [10, 290]

        def source(case):
            return f"""
                PUSH 10
                LOAD $v0 {case}
                LOAD $v1 $v0
            """

        def check(case):
            self.assertRegisters({"$v0": case, "$v1": case})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([0, 0, 0, 0, 10, 0])

        self.run_and_check(cases, source, check)