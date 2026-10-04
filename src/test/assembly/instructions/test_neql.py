from src.test.test_assembler import TestAssembler


class TestNeql(TestAssembler):

    cases = [
        (0, 0), (0, 10), (0, 290),
        (10, 0), (10, 10), (10, 290),
        (290, 0), (290, 10), (290, 290)
    ]

    def test_neql_rt_imm(self):

        def source(case):
            return f"""
                PUSH 10
                LOAD $v1 {case[0]}
                NEQL $v1 {case[1]}
            """

        def check(case):
            self.assertRegisters({"$v1": 1 if case[0] != case[1] else 0 })
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([0, 0, 10, 0])

        self.run_and_check(self.cases, source, check)

    def test_neql_sp_imm(self):
        def source(case):
            return f"""
                PUSH 10
                PUSH {case[0]}
                NEQL $sp {case[1]}
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents([0, 0, 10, 0, 1 if case[0] != case[1] else 0, 0])

        self.run_and_check(self.cases, source, check)
