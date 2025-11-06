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

    def test_load_16bit(self):
        cases = [0, 1, 5, 254, 255, 256, 3000, 65535, 65536]

        for case in cases:
            with self.subTest(load=case):
                self.setUp()
                self.interpreter.run(self.assembler.load(case, bitwidth=16))
                result = self.interpreter.memory[:5]
                self.assertEqual(case % 65536, result[0] + (result[1] * 256), msg=result)
                self.assertEqual([0, 0, 0], result[2:])
                self.assertEqual(4, self.assembler.stack_pointer)

    def test_plus_16bit(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)]

        for case in cases:
            with self.subTest(left=case[0], right=case[1]):
                self.setUp()
                source = ''.join([
                    self.assembler.load(case[0], bitwidth=16),
                    self.assembler.load(case[1], bitwidth=16),
                    self.assembler.plus(bitwidth=16)
                ])
                self.interpreter.run(source)
                result = self.interpreter.memory[:8]
                self.assertEqual((case[0] + case[1]) % 65536, result[0] + (result[1] * 256), msg=result)
                self.assertEqual([0, 0, 0, 0, 0, 0], result[2:])
                self.assertEqual(4, self.assembler.stack_pointer)

    def test_minus_16bit(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)]

        for case in cases:
            with self.subTest(left=case[0], right=case[1]):
                self.setUp()
                source = ''.join([
                    self.assembler.load(case[0], bitwidth=16),
                    self.assembler.load(case[1], bitwidth=16),
                    self.assembler.minus(bitwidth=16)
                ])
                self.interpreter.run(source)
                result = self.interpreter.memory[:8]
                self.assertEqual((case[0] - case[1]) % 65536, result[0] + (result[1] * 256), msg=result)
                self.assertEqual([0, 0, 0, 0, 0, 0], result[2:])
                self.assertEqual(4, self.assembler.stack_pointer)

    def test_logical_not(self):

        cases = [[5, 0],
                 [255, 0],
                 [1, 0],
                 [0, 1],
        ]

        for case in cases:
            subassembler = Assembler()
            source = ''.join([
                subassembler.load(case[0]),
                subassembler.logical_not()
            ])
            self.interpreter.run(source)
            self.assertEqual(self.interpreter.memory[0], case[1], msg=case)
            self.assertEqual(self.interpreter.memory[1], 0, msg=case)
            self.assertEqual(subassembler.stack_pointer, 1, msg=case)

    def test_equals(self):

        cases = [[5, 5, True],
                 [0, 5, False],
                 [5, 0, False],
                 [0, 0, True],
                 [5, 4, False],
                 [255, 4, False],
                 [5, 255, False],
                 [0, 255, False],
                 [255, 0, False],
                 [255, 255, True],
        ]

        for case in cases:
            subassembler = Assembler()
            source = ''.join([
                subassembler.load(case[0]),
                subassembler.load(case[1]),
                subassembler.equals()
            ])
            self.interpreter.run(source)
            self.assertEqual(self.interpreter.memory[0], 1 if case[2] else 0, msg=case)
            self.assertEqual(self.interpreter.memory[1], 0, msg=case)
            self.assertEqual(subassembler.stack_pointer, 1, msg=case)

    def test_push_8bit(self):
        cases = [(0, 0, 0), (1, 0, 0), (5, 5, 5), (255, 0, 0), (0, 0, 255), (255, 255, 255)]

        for case in cases:
            with self.subTest(values=case):
                self.setUp()
                source = ''.join([
                    self.assembler.aloc('x1', 1),
                    self.assembler.aloc('x2', 1),
                    self.assembler.aloc('x3', 1),
                    self.assembler.setvar(self.assembler.vtable['x1'], case[0], bitwidth=8),
                    self.assembler.setvar(self.assembler.vtable['x2'], case[1], bitwidth=8),
                    self.assembler.setvar(self.assembler.vtable['x3'], case[2], bitwidth=8),
                    self.assembler.push(self.assembler.vtable['x1'], bitwidth=8),
                    self.assembler.push(self.assembler.vtable['x2'], bitwidth=8),
                    self.assembler.push(self.assembler.vtable['x3'], bitwidth=8),
                ])
                self.interpreter.run(source)
                result = self.interpreter.memory[:6]
                self.assertListEqual(list(case + case), result)
                self.assertEqual(6, self.assembler.stack_pointer)

    def test_push_16bit(self):
        cases = [(0, 0, 0), (1, 0, 0), (5, 5, 5), (255, 0, 0), (0, 0, 255), (255, 255, 255),
                 (0, 256, 3000), (255, 256, 65535)
        ]

        for case in cases:
            with self.subTest(values=case):
                self.setUp()
                source = ''.join([
                    self.assembler.aloc('x1', 1, bitwidth=16),
                    self.assembler.aloc('x2', 1, bitwidth=16),
                    self.assembler.aloc('x3', 1, bitwidth=16),
                    self.assembler.setvar(self.assembler.vtable['x1'], case[0], bitwidth=16),
                    self.assembler.setvar(self.assembler.vtable['x2'], case[1], bitwidth=16),
                    self.assembler.setvar(self.assembler.vtable['x3'], case[2], bitwidth=16),
                    self.assembler.push(self.assembler.vtable['x1'], bitwidth=16),
                    self.assembler.push(self.assembler.vtable['x2'], bitwidth=16),
                    self.assembler.push(self.assembler.vtable['x3'], bitwidth=16),
                ])
                self.interpreter.run(source)
                self.assertEqual16bit(case[0], self.assembler.vtable['x1'])
                self.assertEqual16bit(case[1], self.assembler.vtable['x2'])
                self.assertEqual16bit(case[2], self.assembler.vtable['x3'])
                self.assertEqual16bit(case[0], self.assembler.vtable['x1'] + 12)
                self.assertEqual16bit(case[1], self.assembler.vtable['x2'] + 12)
                self.assertEqual16bit(case[2], self.assembler.vtable['x3'] + 12)
                self.assertEqual(24, self.assembler.stack_pointer)

    def test_setvar_8bit(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        for case in cases:
            with self.subTest(add=case):
                self.setUp()
                self.interpreter.run(''.join([
                    self.assembler.aloc('x', 1, bitwidth=8),
                    self.assembler.setvar(self.assembler.vtable['x'], 5, bitwidth=8),
                    self.assembler.setvar(self.assembler.vtable['x'], case, bitwidth=8)
                ]))
                result = self.interpreter.memory[:4]
                self.assertEqual(case % 256, result[0], msg=result)
                self.assertEqual([0, 0, 0], result[1:])
                self.assertEqual(1, self.assembler.stack_pointer)

    def assertEqual16bit(self, expected, i):
        self.assertEqual(expected, self.interpreter.memory[i] + (self.interpreter.memory[i+1] * 256))