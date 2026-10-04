from src.test.test_assembler import TestAssembler


class TestSwap(TestAssembler):

    def test_swap_sp_sp(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 10), (255, 0), (0, 255), (255, 255),
                 (3000, 6), (6, 3000), (65536, 0)]

        def source(case):
            return f"""
                PUSH {case[0]}
                PUSH {case[1]}
                SWAP $sp $sp
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents(self.to16bit(case[1]) + self.to16bit(case[0]))

        self.run_and_check(cases, source, check)



