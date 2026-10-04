import unittest

from src.test.test_assembler import TestAssembler


class TestPops(TestAssembler):

    def test_pops_rt(self):
        cases = [0, 1, 5, 255, 3000, 65535]

        def source(case):
            return f"""
                 PUSH 5
                 PUSH {case}
                 POPS $v1
             """

        def check(case):
            self.assertRegisters({"$v1": case})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([0, 0, 5, 0])

        self.run_and_check(cases, source, check)

    def test_pops(self):
        cases = []

        def source(case):
            return f"""
                 PUSH 5
                 PUSH 255
                 POPS
             """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([0, 0, 5, 0])

        self.run_and_check(cases, source, check)



