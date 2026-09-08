from unittest import TestCase

from src.parsers.brainfuckparser import BrainfuckParser, OBFToken


class TestParser(TestCase):

    def setUp(self) -> None:
        self.parser = BrainfuckParser()

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
                result = BrainfuckParser.run(case[0])
                self.assertListEqual(result, case[1])
