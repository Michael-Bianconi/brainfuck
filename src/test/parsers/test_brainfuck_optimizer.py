from unittest import TestCase

from src.assembly.assembler import Assembler
from src.parsers.brainfuck_optimizer import BrainfuckOptimizer, OBFToken


class TestBrainfuckOptimizer(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()
        self.parser = BrainfuckOptimizer()

    def test_mmv(self):
        cases = [
            ("[->+>+<<]", [OBFToken('mmv', [1, 1])]),
            ("[->>+>+<<<]", [OBFToken('mmv', [2, 1])]),
            ("[-<+>>+<]", [OBFToken('mmv', [-1, 2])]),
            ("[>+>+<<-]", [OBFToken('mmv', [1, 1])]),
            ("[>>>+<<<<<+>>-]", [OBFToken('mmv', [3, -5])]),
        ]
        for case in cases:
            with self.subTest(values=case):
                result = BrainfuckOptimizer.run(case[0])
                self.assertListEqual(result, case[1])

    def test_mov(self):
        cases = [
            ("[->+<]", [OBFToken('mov', [1])]),
            ("[->>+<<]", [OBFToken('mov', [2])]),
            ("[-<+>]", [OBFToken('mov', [-1])]),
            ("[>>>>>>+<<<<<<-]", [OBFToken('mov', [6])]),
            ("[->>>>>>+<<<<<<]", [OBFToken('mov', [6])]),
        ]
        for case in cases:
            with self.subTest(values=case):
                result = BrainfuckOptimizer.run(case[0])
                self.assertListEqual(result, case[1])

    def test_jfz_jbn(self):
        cases = [
            ("++--[>++<-]", """
            inc 2
            inc -2
            jfz 5
            mdp 1
            inc 2
            mdp -1
            inc -1
            jbn 5
            """)
        ]

        for case in cases:
            with self.subTest(values=case):
                expected = BrainfuckOptimizer.load_bfo(case[1])
                result = BrainfuckOptimizer.run(case[0])
                self.assertListEqual(result, expected)

    def test_cpy(self):
        cases = [
            (self.assembler.assemble("_CPY 3 5"), "cpy 3 5"),
            (self.assembler.assemble("_CPY -1 1000"), "cpy -1 1000"),
            (self.assembler.assemble("_CPY 2 -4"), "cpy 2 -4"),
            (self.assembler.assemble("_CPY -3 5"), "cpy -3 5"),
        ]

        for case in cases:
            with self.subTest(values=case):
                expected = BrainfuckOptimizer.load_bfo(case[1])
                result = BrainfuckOptimizer.run(case[0])
                self.assertListEqual(result, expected, msg=case[0])