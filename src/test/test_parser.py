from unittest import TestCase
import pyparsing as pp

from src.assembly.parser import Parser, Operand


class TestParser(TestCase):

    def setUp(self) -> None:
        self.parser = Parser()

    def test_parse_no_operands(self):
        source = "POPN"
        for line in self.parser.parse(source):
            self.assertEqual("POPN", line["Mnemonic"])
            self.assertEqual(0, len(line["Operands"]))

    def test_parse_imm_imm(self):
        source = "MNEM 4 -8"
        self.parser.parse(source).__next__()
        left, right = self.parser.operands()
        self.assertEqual("MNEM", self.parser.mnemonic())
        self.assertEqual(2, self.parser.operand_count())
        self.assertEqual(4, left.resolve({}))
        self.assertEqual(-8, right.resolve({}))

    def test_parse_address(self):

        cases = [
            ("@5", 5),
            ("@a", 2),
            ("&a", 2)
        ]

        for case in cases:
            with self.subTest(case=case):
                operand, expected = case
                source = "NULL " + operand
                self.parser.parse(source).__next__()
                [out] = self.parser.operands()
                print(self.parser.dump())
                self.assertEqual("NULL", self.parser.mnemonic())
                self.assertEqual(1, self.parser.operand_count())
                self.assertEqual(expected, out.resolve({"a": 2}))

    def test_parse_top(self):
        cases = [
            "@top"
        ]

        for case in cases:
            with self.subTest(case=case):
                source = "NULL " + case
                self.parser.parse(source).__next__()
                [out] = self.parser.operands()
                self.assertEqual("NULL", self.parser.mnemonic())
                self.assertEqual(1, self.parser.operand_count())
                self.assertEqual("top", out.resolve({}))

    def test_multi_instruction(self):
        source = """
            OPRA 5 15
            OPRB 10 20
            """
        self.parser.parse(source)
        self.parser.__next__()
        self.assertEqual("OPRA", self.parser.mnemonic())
        self.assertEqual(5, self.parser.operands()[0].resolve({}))
        self.assertEqual(15, self.parser.operands()[1].resolve({}))
        self.assertEqual(2, len(self.parser.operands()))
        self.parser.__next__()
        self.assertEqual("OPRB", self.parser.mnemonic())
        self.assertEqual(10, self.parser.operands()[0].resolve({}))
        self.assertEqual(20, self.parser.operands()[1].resolve({}))
        self.assertEqual(2, len(self.parser.operands()))

    def test_raw(self):
        source = "_RAW >>+"
        self.parser.parse(source).__next__()
        self.assertEqual("_RAW", self.parser.mnemonic())
        self.assertEqual(1, self.parser.operand_count())
        self.assertEqual(">>+", self.parser.operands()[0].resolve({}))

    def test_comment(self):
        source = f"""
        # just a comment
        PUSH @top @top @top
        """
        self.parser.parse(source)
