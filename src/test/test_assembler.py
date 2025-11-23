from unittest import TestCase

from src.assembly.assembler import Assembler
from src.interpreter import Interpreter


class TestAssembler(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()
        self.interpreter = Interpreter()

    # def test_logical_not(self):
    #     cases = [0, 1, 2, 5, 255]
    #
    #     def source(case, offset=0):
    #         return ''.join([
    #                 self.assembler.load(case),
    #                 self.assembler.logical_not()
    #         ])
    #
    #     def check(case, offset=0):
    #         self.assertStackContents([0 if case > 0 else 1], 1+offset)
    #
    #     self.run_and_check(cases, source, check)
    #
    #
    #
    #
    # def test_if_nonzero(self):
    #
    #     cases = [0, 1, 255]
    #
    #     def source(case, offset=0):
    #         return ''.join([
    #             self.assembler.load(5),
    #             self.assembler.load(case),
    #             self.assembler.if_nonzero(),
    #             self.assembler.load(5),
    #             self.assembler.plus(8, 8, 8),
    #             self.assembler.end_if()
    #         ])
    #
    #     def check(case, offset=0):
    #         self.assertStackContents([10 if case > 0 else 5], 1+offset)
    #
    #     self.run_and_check(cases, source, check)
    #
    # def test_if_zero(self):
    #
    #     cases = [0, 1, 255]
    #
    #     def source(case, offset=0):
    #         return ''.join([
    #             self.assembler.load(5),
    #             self.assembler.load(case),
    #             self.assembler.if_zero(),
    #             self.assembler.load(5),
    #             self.assembler.plus(8, 8, 8),
    #             self.assembler.end_if()
    #         ])
    #
    #     def check(case, offset=0):
    #         self.assertStackContents([10 if case == 0 else 5], 1+offset)
    #
    #     self.run_and_check(cases, source, check)
    #
    # def test_if_nonzero_else(self):
    #
    #     cases = [0, 1, 255]
    #
    #     def source(case, offset=0):
    #         return ''.join([
    #             self.assembler.load(5),
    #             self.assembler.load(case),
    #             self.assembler.if_nonzero(),
    #                 self.assembler.load(5),
    #                 self.assembler.plus(8, 8, 8),
    #             self.assembler.else_block(),
    #                 self.assembler.load(1),
    #                 self.assembler.plus(8, 8, 8),
    #             self.assembler.end_if(),
    #             self.assembler.load(1),
    #             self.assembler.plus(8, 8, 8)
    #         ])
    #
    #     def check(case, offset=0):
    #         self.assertStackContents([11 if case > 0 else 7], 1+offset)
    #
    #     self.run_and_check(cases, source, check)
    #
    # def test_while_nonzero(self):
    #     cases = [0, 1, 5, 250]
    #
    #     def source(case, offset=0):
    #         return ''.join([
    #             self.assembler.load(case),
    #             self.assembler.load(5),
    #             self.assembler.while_nonzero(offset),
    #             self.assembler.load(1),
    #             self.assembler.plus(8, 8, 8),
    #             self.assembler.end_while(offset)
    #         ])
    #
    #     def check(case, offset):
    #         self.assertStackContents([0,5+case], 2+offset)
    #
    #     self.run_and_check(cases, source, check)
    #
    # def test_less_than(self):
    #     cases = [[0, 0], [0, 1], [1, 1], [1, 5], [5, 255], [255, 255]]
    #     cases.extend([c[::-1] for c in cases if c[0] != c[1]])
    #
    #     def source(case, offset):
    #         return ''.join([
    #             self.assembler.load(case[0]),
    #             self.assembler.load(case[1]),
    #             self.assembler.less_than(),
    #         ])
    #
    #     def check(case, offset):
    #         self.assertStackContents([1 if case[0] < case[1] else 0], 1+offset)
    #
    #     self.run_and_check(cases, source, check)
    #
    # def test_greater_than(self):
    #     cases = [[0, 0], [0, 1], [1, 1], [1, 5], [5, 255], [255, 255]]
    #     cases.extend([c[::-1] for c in cases if c[0] != c[1]])
    #
    #     def source(case, offset):
    #         return ''.join([
    #             self.assembler.load(case[0]),
    #             self.assembler.load(case[1]),
    #             self.assembler.greater_than(),
    #         ])
    #
    #     def check(case, offset):
    #         self.assertStackContents([1 if case[0] > case[1] else 0], 1+offset)
    #
    #     self.run_and_check(cases, source, check)
    #
    def test_fibonacci(self):

        cases = [0, 1, 2, 5, 9]

        def source(case):
            return f"""
                ALOC left 1
                ALOC right 1
                ALOC stage 1
                FUNC next
                    PUSH @top @left
                    PUSH @top @right
                    PUSH @top @left
                    PLUS @top @top @top
                    POPV @right @top
                    POPV @left @top
                    PLUS @stage @stage 1
                    PUSH {case}
                    EQLS @top @top @top
                    RTRN
                PUSH @left 0
                PUSH @right 1
                PUSH @top @stage
                PUSH @top {case}
                EQLS @top @top @top
                _RAW <[>
                    CINZ @top next
                _RAW <]>
                POPV @top        
            """

        def check(case):
            self.assertStackContents([])

    def assertStackContents(self, expected_content, expected_pointer):
        """

        :param expected_content: The top n values on the stack.
        :param expected_pointer: The position of the stack pointer.
        :return:
        """
        start = self.assembler.stack_pointer - len(expected_content)
        actual_content = self.interpreter.memory[start:self.assembler.stack_pointer]
        self.assertListEqual(actual_content, expected_content, msg=self.dump_interpreter())
        self.assertEqual(self.assembler.stack_pointer, expected_pointer, msg=self.dump_interpreter())
        self.assertListEqual(self.interpreter.memory[expected_pointer:expected_pointer+10], [0] * 10,
                             msg='Expected cells past stack pointer to be empty' + self.dump_interpreter())
        self.assertEqual(self.assembler.stack_pointer, self.interpreter.dptr)

    def to16bit(self, i):
        lo = (i % 65536) & 0b0000000011111111
        hi = ((i % 65536) & 0b1111111100000000) >> 8
        return [lo, hi, 0, 0]

    def dump_interpreter(self):
        memory = ''
        pointers = ''
        for i in range(self.assembler.stack_pointer + 10):
            cell = str(self.interpreter.memory[i])
            memory += cell + ' '
            pointers += 's' if i == self.assembler.stack_pointer else 'd' if i == self.interpreter.dptr else ' '
            pointers += ' ' * len(cell)

        return '\n' + memory + '\n' + pointers

    def cases_immediate8(self):
        return [0, 1, 5, 255]

    def cases_immediate8_immediate8(self):
        return [
            [0, 0], [0, 1], [1, 0], [1, 1], [5, 10], [255, 0], [0, 255], [255, 255]
        ]

    def run_and_check(self, cases, source, check):
        for case in cases:
            with self.subTest(values=case):
                self.setUp()
                exe = self.assembler.assemble(source(case))
                self.interpreter.run(exe)
                check(case)
