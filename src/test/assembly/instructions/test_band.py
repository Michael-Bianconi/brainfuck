import unittest

from src.test.test_assembler import TestAssembler


class TestBand(TestAssembler):

    cases = [
        (0, 0), (0, 0x00FF), (0, 0xFF00), (0, 0xFFFF),
        (10, 0), (10, 0x00FF), (10, 0xFF00), (10, 0xFFFF),
        (255, 0), (255, 0x00FF), (255, 0xFF00), (255, 0xFFFF),
        (4000, 0), (4000, 0x00FF), (4000, 0xFF00), (4000, 0xFFFF),
    ]

    def test_band_sp_imm(self):

        def source(case):
            return f"""
                PUSH 10
                PUSH {case[0]}
                BAND $sp {case[1]} 
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents([10, 0] + self.to16bit(case[0] & case[1]))

        self.run_and_check(self.cases, source, check)

    def test_band_rt_imm(self):

        def source(case):
            return f"""
                PUSH 10
                LOAD $v1 {case[0]}
                BAND $v1 {case[1]} 
            """

        def check(case):
            self.assertRegisters({"$v1": case[0] & case[1]})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([10, 0])

        self.run_and_check(self.cases, source, check)


