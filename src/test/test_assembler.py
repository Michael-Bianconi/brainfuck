from unittest import TestCase

from src.assembler import Assembler
from src.interpreter import Interpreter


class TestAssembler(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()
        self.interpreter = Interpreter()

    def test_add_8bit(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        for case in cases:
            with self.subTest(add=case):
                self.setUp()
                self.interpreter.run(self.assembler.add(case, bitwidth=8))
                result = self.interpreter.memory[:4]
                self.assertEqual(case % 256, result[0], msg=result)
                self.assertEqual([0, 0, 0], result[1:])
                self.assertEqual(0, self.assembler.stack_pointer)

    def test_add_16bit(self):
        cases = [0, 1, 5, 255, 256, 3000, 65535, 65536, 65540]

        for case in cases:
            with self.subTest(add=case):
                self.setUp()
                source = self.assembler.add(case, bitwidth=16)
                self.interpreter.run(source)
                result = self.interpreter.memory[:4]
                self.assertEqual(case % 65536, result[0] + (result[1] * 256), msg=result)
                self.assertEqual([0, 0], result[2:])
                self.assertEqual(0, self.assembler.stack_pointer)

    def test_sub_16bit(self):
        cases = [
            (1, 0), (5, 0), (255, 0), (65535, 0),
            (1, 1), (5, 1), (5, 3), (5, 5), (255, 255),
            (257, 1), (257, 5), (3000, 2000), (65535, 2),
            (0, 1), (0, 5), (5, 10), (255, 256)
        ]

        for case in cases:
            with self.subTest(initial=case[0], subtract=case[1]):
                self.setUp()
                self.interpreter.run(self.assembler.add(case[0], bitwidth=16) + self.assembler.sub(case[1], bitwidth=16))
                result = self.interpreter.memory[:4]
                self.assertEqual((case[0] - case[1]) % 65536, result[0] + (result[1] * 256), msg=result)
                self.assertEqual([0, 0], result[2:])
                self.assertEqual(0, self.assembler.stack_pointer)

    def test_load_8bit(self):
        cases = [0, 1, 5, 254, 255]

        def source(case, offset=0):
            return self.assembler.load(case, bitwidth=8)

        def check(case, offset=0):
            self.assertStackContents([case], offset+1)

        self.run_and_check(cases, source, check)

    def test_load_16bit(self):
        cases = [0, 1, 5, 254, 255, 256, 3000, 65535, 65536]

        def source(case, offset=0):
            return self.assembler.load(case, bitwidth=16)

        def check(case, offset=0):
            lo = case & 0b0000000011111111
            hi = (case & 0b1111111100000000) >> 8
            self.assertStackContents([lo, hi, 0, 0], 4+offset)

        self.run_and_check(cases, source, check)

    def test_plus_16bit(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)
        ]

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case[0], bitwidth=16),
                    self.assembler.load(case[1], bitwidth=16),
                    self.assembler.plus(16,16,16)
            ])

        def check(case, offset=0):
            lo = sum(case) & 0b0000000011111111
            hi = (sum(case) & 0b1111111100000000) >> 8
            self.assertStackContents([lo, hi, 0, 0], 4+offset)

        self.run_and_check(cases, source, check)

    def test_minus_16bit(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)]

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case[0], bitwidth=16),
                    self.assembler.load(case[1], bitwidth=16),
                    self.assembler.minus(16)
            ])

        def check(case, offset=0):
            lo = ((case[0]-case[1]) % 65536) & 0b0000000011111111
            hi = (((case[0]-case[1]) % 65536) & 0b1111111100000000) >> 8
            self.assertStackContents([lo, hi, 0, 0], 4+offset)

        self.run_and_check(cases, source, check)

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

    def test_push_8bit(self):
        cases = [(0, 0, 0), (1, 0, 0), (5, 5, 5), (255, 0, 0), (0, 0, 255), (255, 255, 255)]

        def source(case, offset=0):
            return ''.join([
                        self.assembler.load(case[0], bitwidth=8),
                        self.assembler.load(case[1], bitwidth=8),
                        self.assembler.load(case[2], bitwidth=8),
                        self.assembler.push(offset, bitwidth=8),
                        self.assembler.push(offset+1, bitwidth=8),
                        self.assembler.push(offset+2, bitwidth=8),
            ])

        def check(case, offset):
            self.assertStackContents(list(case + case), 6 + offset)

        self.run_and_check(cases, source, check)

    def test_push_16bit(self):
        cases = [(0, 0, 0), (1, 0, 0), (5, 5, 5), (255, 0, 0), (0, 0, 255), (255, 255, 255),
                 (0, 256, 3000), (255, 256, 65535)
        ]

        def source(case, offset=0):
            return ''.join([
                    self.assembler.load(case[0], bitwidth=16),
                    self.assembler.load(case[1], bitwidth=16),
                    self.assembler.load(case[2], bitwidth=16),
                    self.assembler.push(offset, bitwidth=16),
                    self.assembler.push(offset+4, bitwidth=16),
                    self.assembler.push(offset+8, bitwidth=16),
            ])

        def check(case, offset=0):
            expected = []
            for i in case + case:
                expected.extend(self.to16bit(i))
            self.assertStackContents(expected, 24 + offset)

        self.run_and_check(cases, source, check)

    def test_setvar_8bit(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        def source(case, offset=0):
            return ''.join([
                    self.assembler.aloc('x', 1, bitwidth=8),
                    self.assembler.setvar(self.assembler.vtable['x'], 5, bitwidth=8),
                    self.assembler.setvar(self.assembler.vtable['x'], case, bitwidth=8)
            ])

        def check(case, offset=0):
            self.assertStackContents([case % 256], 1+offset)

        self.run_and_check(cases, source, check)

    def test_swap_8bit(self):

        cases = [[5, 5], [0, 5], [0, 0], [5, 4], [255, 4], [5, 255], [0, 255], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case, offset=0):
            return ''.join([
                self.assembler.load(case[0]),
                self.assembler.load(case[1]),
                self.assembler.swap(bitwidth=8)
            ])

        def check(case, offset=0):
            self.assertStackContents(case[::-1], 2+offset)

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

    def test_if_equal(self):

        cases = [[0, 0], [0, 1], [0, 255], [1, 1], [1, 5], [5, 255], [255, 255]]
        cases.extend([c[::-1] for c in cases])

        def source(case, offset=0):
            return ''.join([
                self.assembler.load(5),
                self.assembler.load(case[0]),
                self.assembler.load(case[1]),
                self.assembler.if_equal(),
                self.assembler.load(5),
                self.assembler.plus(8, 8, 8),
                self.assembler.end_if()
            ])

        def check(case, offset=0):
            self.assertStackContents([10 if case[0] == case[1] else 5], 1+offset)

        self.run_and_check(cases, source, check)

    def assertStackContents(self, expected_content, expected_pointer):
        """

        :param expected_content: The top n values on the stack.
        :param expected_pointer: The position of the stack pointer.
        :return:
        """
        start = self.assembler.stack_pointer - len(expected_content)
        actual_content = self.interpreter.memory[start:self.assembler.stack_pointer]
        self.assertEqual(self.assembler.stack_pointer, expected_pointer, msg=actual_content)
        self.assertListEqual(actual_content, expected_content)
        self.assertListEqual(self.interpreter.memory[expected_pointer:expected_pointer+10], [0] * 10,
                             msg='Expected cells past stack pointer to be empty')

    def to16bit(self, i):
        lo = (i % 65536) & 0b0000000011111111
        hi = ((i % 65536) & 0b1111111100000000) >> 8
        return [lo, hi, 0, 0]

    def run_and_check(self, cases, source, check):
        for case in cases:
            for noise in [[], [0], [1], [0,1], [1,0], [1,1]]:
                with self.subTest(values=case, noise=noise):
                    self.setUp()
                    self.interpreter.run(
                        ''.join([self.assembler.load(n) for n in noise]) +
                        source(case, offset=len(noise)))
                    check(case, offset=len(noise))
