import unittest

from src.test.test_assembler import TestAssembler


class TestMemoryMixin(TestAssembler):

    def test_swap_top_top(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 10), (255, 0), (0, 255), (255, 255),
                 (3000, 6), (6, 3000), (65536, 0)]

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                SWAP @top @top
            """

        def check(case):
            self.assertStackContents(self.to16bit(case[1]) + self.to16bit(case[0]) + self.to16bit(4), 4)

        self.run_and_check(cases, source, check)

    def test_popv_16_top(self):
        cases = [0, 1, 2, 255, 3000, 65535]

        def source(case):
            return f"""
                PUSH @top 5
                PUSH @top {case}
                POPV @top
            """

        def check(case):
            self.assertStackContents([5, 0], 2)

        self.run_and_check(cases, source, check)

        def check(case):
            self.assertStackContents([0, case % 256, 0], 3)

        self.run_and_check(cases, source, check)

    def test_popv_16_address_top(self):
        cases = [0, 1, 5, 255, 3000, 65535]

        def source(case):
            return f"""
                 ALOC a 1
                 ALOC b 1
                 PUSH @b 258
                 PUSH @top {case}
                 POPV @b @top
             """

        def check(case):
            expected = [0, 0] + self.to16bit(case)
            self.assertStackContents(expected, 4)

        self.run_and_check(cases, source, check)



