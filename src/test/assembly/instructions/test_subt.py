from src.test.test_assembler import TestAssembler


class TestSubt(TestAssembler):

    def test_subt_sp_sp_sp(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1), (268, 255),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)]

        def source(case):
            return f"""
                PUSH 10
                PUSH {case[0]}
                PUSH {case[1]}
                SUBT $sp $sp $sp
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents([10, 0] + self.to16bit(case[0]-case[1]))

        self.run_and_check(cases, source, check)
