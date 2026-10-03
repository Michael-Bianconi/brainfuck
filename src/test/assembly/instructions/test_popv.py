import unittest

from src.test.test_assembler import TestAssembler


class TestMemoryMixin(TestAssembler):

    def test_popv_rt(self):
        cases = [0, 1, 5, 255, 3000, 65535]

        def source(case):
            return f"""
                 PUSH 5
                 PUSH {case}
                 POPV $v1
             """

        def check(case):
            self.assertRegisters({"$v1": case})
            self.assertDataPointerAlignsWithStackPointer(2)
            self.assertStackContents([0, 0, 5, 0])

        self.run_and_check(cases, source, check)



