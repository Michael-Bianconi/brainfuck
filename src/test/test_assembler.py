from unittest import TestCase

from src.assembly.assembler import Assembler
from src.interpreter import Interpreter


class TestAssembler(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()
        self.interpreter = Interpreter()

    def test_multiply_8bit(self):
        cases = [[0, 0], [1, 0], [1, 1], [1, 5], [1, 255], [5, 5], [30, 3], [30, 30], [255, 0], [255, 1], [255, 255]]
        cases.extend([c[::-1] for c in cases])

        def source(case, offset=0):
            return ''.join([
                self.assembler.load(case[0]),
                self.assembler.load(case[1]),
                self.assembler.multiply()
            ])

        def check(case, offset=0):
            self.assertStackContents([(case[0] * case[1]) % 256], 1+offset)
            self.assertEqual((case[0]+1)+(case[1]+1)+(7*case[1]), self.interpreter.cycles)

        self.run_and_check(cases, source, check)

    def test_logical_not(self):
        cases = [0, 1, 2, 5, 255]

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case),
                    self.assembler.logical_not()
            ])

        def check(case, offset=0):
            self.assertStackContents([0 if case > 0 else 1], 1+offset)

        self.run_and_check(cases, source, check)

    def test_logical_and(self):
        cases = [[0, 0], [1, 0], [5, 0], [255, 0], [1, 1], [5, 5], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case[0], bitwidth=8),
                    self.assembler.load(case[1], bitwidth=8),
                    self.assembler.logical_and(bitwidth=8)
            ])

        def check(case, offset=0):
            self.assertStackContents([(case[0] > 0 and case[1] > 0)], 1+offset)

        self.run_and_check(cases, source, check)

    def test_logical_or(self):
        cases = [[0, 0], [1, 0], [5, 0], [255, 0], [1, 1], [5, 5], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case[0], bitwidth=8),
                    self.assembler.load(case[1], bitwidth=8),
                    self.assembler.logical_or(bitwidth=8)
            ])

        def check(case, offset=0):
            self.assertStackContents([(case[0] > 0 or case[1] > 0)], 1+offset)

        self.run_and_check(cases, source, check)

    def test_equals_8bit(self):

        cases = [[5, 5], [0, 5], [0, 0], [5, 4], [255, 4], [5, 255], [0, 255], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case[0]),
                    self.assembler.load(case[1]),
                    self.assembler.equals()
            ])

        def check(case, offset=0):
            self.assertStackContents([1 if case[0] == case[1] else 0], 1+offset)

        self.run_and_check(cases, source, check)

    def test_equals_16bit(self):

        cases = [[5, 5], [0, 5], [0, 0], [5, 4], [255, 4], [5, 255], [0, 255], [255, 255],
                 [0, 256], [0, 3000], [0, 65535], [256, 256, 65535]]
        cases.extend([x[::-1] for x in cases])

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case[0], bitwidth=16),
                    self.assembler.load(case[1], bitwidth=16),
                    self.assembler.equals(bitwidth=16)
            ])

        def check(case, offset=0):
            self.assertStackContents([1 if case[0] == case[1] else 0], 1+offset)

        self.run_and_check(cases, source, check)

    def test_get_indirect(self):
        arrays = [
            [[1], 0],
            [[1, 2, 3, 4, 5], 0],
            [[1, 2, 3, 4, 5], 4],
        ]
        cases = []
        for array in arrays:
            for after in [[], [0], [1], [0,1],[1,0],[1,1]]:
                cases.append([array, after])

        def source(case, offset=0):
            [data, index], suffix = case
            return ''.join([
                ''.join([self.assembler.load(x) for x in data]),
                ''.join([self.assembler.load(x) for x in suffix]),
                self.assembler.load(index),
                self.assembler.get_indirect(offset, bitwidth=8)
            ])

        def check(case, offset=0):
            [data, index], suffix = case
            self.assertStackContents(data + suffix + [data[index]], len(data + suffix) + 1 + offset)

        self.run_and_check(cases, source, check)

    def test_set_indirect(self):
        arrays = [
            [[1], 5, 0],
            [[1, 2, 3, 4, 5], 5, 0],
            [[1, 2, 3, 4, 5], 5, 2],
        ]
        cases = []
        for array in arrays:
            for after in [[], [0], [1], [0,1],[1,0],[1,1]]:
                cases.append([array, after])

        def source(case, offset=0):
            [data, value, index], suffix = case
            return ''.join([
                ''.join([self.assembler.load(x) for x in data]),
                ''.join([self.assembler.load(x) for x in suffix]),
                self.assembler.load(value),
                self.assembler.load(index),
                self.assembler.set_indirect(offset, bitwidth=8),
                self.assembler.load(255)
            ])

        def check(case, offset=0):
            [data, value, index], suffix = case
            data[index] = value
            self.assertStackContents(data + suffix + [255], len(data + suffix) + 1 + offset)

        self.run_and_check(cases, source, check)

    def test_if_nonzero(self):

        cases = [0, 1, 255]

        def source(case, offset=0):
            return ''.join([
                self.assembler.load(5),
                self.assembler.load(case),
                self.assembler.if_nonzero(),
                self.assembler.load(5),
                self.assembler.plus(8, 8, 8),
                self.assembler.end_if()
            ])

        def check(case, offset=0):
            self.assertStackContents([10 if case > 0 else 5], 1+offset)

        self.run_and_check(cases, source, check)

    def test_if_zero(self):

        cases = [0, 1, 255]

        def source(case, offset=0):
            return ''.join([
                self.assembler.load(5),
                self.assembler.load(case),
                self.assembler.if_zero(),
                self.assembler.load(5),
                self.assembler.plus(8, 8, 8),
                self.assembler.end_if()
            ])

        def check(case, offset=0):
            self.assertStackContents([10 if case == 0 else 5], 1+offset)

        self.run_and_check(cases, source, check)

    def test_if_nonzero_else(self):

        cases = [0, 1, 255]

        def source(case, offset=0):
            return ''.join([
                self.assembler.load(5),
                self.assembler.load(case),
                self.assembler.if_nonzero(),
                    self.assembler.load(5),
                    self.assembler.plus(8, 8, 8),
                self.assembler.else_block(),
                    self.assembler.load(1),
                    self.assembler.plus(8, 8, 8),
                self.assembler.end_if(),
                self.assembler.load(1),
                self.assembler.plus(8, 8, 8)
            ])

        def check(case, offset=0):
            self.assertStackContents([11 if case > 0 else 7], 1+offset)

        self.run_and_check(cases, source, check)

    def test_while_nonzero(self):
        cases = [0, 1, 5, 250]

        def source(case, offset=0):
            return ''.join([
                self.assembler.load(case),
                self.assembler.load(5),
                self.assembler.while_nonzero(offset),
                self.assembler.load(1),
                self.assembler.plus(8, 8, 8),
                self.assembler.end_while(offset)
            ])

        def check(case, offset):
            self.assertStackContents([0,5+case], 2+offset)

        self.run_and_check(cases, source, check)

    def test_less_than(self):
        cases = [[0, 0], [0, 1], [1, 1], [1, 5], [5, 255], [255, 255]]
        cases.extend([c[::-1] for c in cases if c[0] != c[1]])

        def source(case, offset):
            return ''.join([
                self.assembler.load(case[0]),
                self.assembler.load(case[1]),
                self.assembler.less_than(),
            ])

        def check(case, offset):
            self.assertStackContents([1 if case[0] < case[1] else 0], 1+offset)

        self.run_and_check(cases, source, check)

    def test_greater_than(self):
        cases = [[0, 0], [0, 1], [1, 1], [1, 5], [5, 255], [255, 255]]
        cases.extend([c[::-1] for c in cases if c[0] != c[1]])

        def source(case, offset):
            return ''.join([
                self.assembler.load(case[0]),
                self.assembler.load(case[1]),
                self.assembler.greater_than(),
            ])

        def check(case, offset):
            self.assertStackContents([1 if case[0] > case[1] else 0], 1+offset)

        self.run_and_check(cases, source, check)

    def test_fibonacci(self):

        cases = [0, 1, 2, 5, 9]

        def source(case):
            return ''.join([
                self.assembler.load(case),
                self.assembler.if_nonzero()

            ])

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
        result = '\n'
        result += ' '.join([str(x) for x in self.interpreter.memory[:self.assembler.stack_pointer + 10]])
        result += '\n'
        result += ' '.join(['s' if i == self.assembler.stack_pointer else 'd' if i == self.interpreter.dptr else ' ' for i in range(self.assembler.stack_pointer + 10)])
        return result

    def run_and_check(self, cases, source, check):
        for case in cases:
            with self.subTest(values=case):
                self.setUp()
                self.interpreter.run(self.assembler.assemble(source(case)))
                check(case)


