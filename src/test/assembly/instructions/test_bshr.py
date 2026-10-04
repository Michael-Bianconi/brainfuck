import unittest

from src.test.test_assembler import TestAssembler


class TestBshr(TestAssembler):

    cases = [
        (0, 0), (0, 8), (0, 16),
        (10, 0), (10, 8), (10, 16),
        (255, 0), (255, 8), (255, 16),
        (4000, 0), (4000, 8), (4000, 16),
    ]

    def test_bshr_sp_imm(self):

        def source(case):
            return f"""
                PUSH 10
                PUSH {case[0]}
                BSHR $sp {case[1]} 
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents([10, 0] + self.to16bit((case[0] << case[1]) % 65536))

        self.run_and_check(self.cases, source, check)

    def test_bshr_rt_imm(self):

        def source(case):
            return f"""
                PUSH 10
                LOAD $v1 {case[0]}
                BSHR $v1 {case[1]} 
            """

        def check(case):
            self.assertRegisters({"$v1": (case[0] << case[1]) % 65536})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([10, 0])

        self.run_and_check(self.cases, source, check)


