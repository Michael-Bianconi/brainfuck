from unittest import TestCase
import pyparsing as pp

from src.assembly.parser import Parser, Immediate, Address, Symbol, Top, Raw


class TestParser(TestCase):

    def setUp(self) -> None:
        self.parser = Parser()

    def test_parse_no_operands(self):
        source = "POPN"
        for line in self.parser.parse(source):
            self.assertEqual("POPN", line["Mnemonic"])
            self.assertEqual(0, len(line["Operands"]))

    def test_parse_imm_imm(self):
        source = "MNEM 4:16 8"
        self.parser.parse(source).__next__()
        left, right = self.parser.operands()
        self.assertEqual("MNEM", self.parser.mnemonic())
        self.assertEqual(2, self.parser.operand_count())
        self.assertEqual(Immediate, type(left))
        self.assertEqual(4, left.value)
        self.assertEqual(16, left.bitwidth)
        self.assertEqual(Immediate, type(right))
        self.assertEqual(8, right.value)
        self.assertEqual(8, right.bitwidth)

    def test_parse_address(self):

        cases = [
            ("@5", (5, 8, 0, 8)),
            ("@5[0]", (5, 8, 0, 8)),
            ("@5[10]", (5, 8, 10, 8)),
            ("@5[10:16]", (5, 8, 10, 16)),
            ("@5[@10:16]", (5, 8, "@10", 16)),
            ("@5[@a:16]", (5, 8, "@a", 16)),
            ("@5:16", (5, 16, 0, 8)),
            ("@5:16", (5, 16, 0, 8)),
            ("@a", ("a", 8, 0, 8)),
            ("@a:16", ("a", 16, 0, 8))
        ]

        for case in cases:
            with self.subTest(case=case):
                operand, (base, base_bitwidth, index, index_bitwidth) = case
                source = "NULL " + operand
                self.parser.parse(source).__next__()
                [out] = self.parser.operands()
                print(self.parser.dump())
                self.assertEqual("NULL", self.parser.mnemonic())
                self.assertEqual(1, self.parser.operand_count())
                self.assertEqual(Address, type(out))
                if int == type(base):
                    self.assertEqual(Immediate, type(out.base))
                else:
                    self.assertEqual(Symbol, type(out.base))
                self.assertEqual(base, out.base.value)
                self.assertEqual(base_bitwidth, out.base.bitwidth)
                if str(index).startswith("@"):
                    self.assertEqual(str(index).startswith("@"), out.indirect)
                self.assertEqual(str(index), ("@" if out.indirect else "") + str(out.index.value))
                self.assertEqual(index_bitwidth, out.index.bitwidth)

    def test_parse_top(self):
        cases = [
            "@top",
            "@top:16",
        ]

        for case in cases:
            with self.subTest(case=case):
                source = "NULL " + case
                expected_bitwidth = int(case.split(':')[1] if ':' in case else '8')
                self.parser.parse(source).__next__()
                [out] = self.parser.operands()
                print(self.parser.dump())
                self.assertEqual("NULL", self.parser.mnemonic())
                self.assertEqual(1, self.parser.operand_count())
                self.assertEqual(Top, type(out))
                self.assertEqual(expected_bitwidth, out.bitwidth)

    def test_parse_top_indirect(self):

        case = "@a[@top]"
        source = "NULL " + case
        expected_bitwidth = int(case.split(':')[1] if ':' in case else '8')
        self.parser.parse(source).__next__()
        [out] = self.parser.operands()
        self.assertEqual("NULL", self.parser.mnemonic())
        self.assertEqual(1, self.parser.operand_count())
        self.assertEqual(Address, type(out))
        self.assertEqual(Top, type(out.index))

    def test_parse_bad_address(self):

        cases = [
            "5[5]",         # Base cannot be an immediate
            "@5[@5[5]]",    # Nested indirect addresses
            "@top[4]",      # Top with index
        ]

        for case in cases:
            with self.subTest(case=case):
                source = "NULL " + case
                self.assertRaises(pp.ParseException, lambda: self.parser.parse(source))

    def test_resolve_direct_address(self):
        vtable = {
            "a": 10
        }

        cases = [
            ("@0", 0),
            ("@0:16", 0),
            ("@5:16", 5),
            ("@16:16", 16),
            ("@a:8[10:16]", 20),
            ("@0:16[0]", 0),
            ("@5:16[12]", 53),
            ("@a:16[10]", 50),
            ("@a:16[10:8]", 50),
        ]

        for case in cases:
            with self.subTest(case=case):
                source = "NULL " + case[0]
                self.parser.parse(source).__next__()
                [actual] = self.parser.operands()
                resolved = case[1]
                self.assertEqual(resolved, actual.resolve_direct(vtable))

    def test_multi_instruction(self):
        source = """
            OPRA 5 15
            OPRB 10 20
            """
        self.parser.parse(source)
        self.parser.__next__()
        self.assertEqual("OPRA", self.parser.mnemonic())
        self.assertEqual(5, self.parser.operands()[0].value)
        self.assertEqual(15, self.parser.operands()[1].value)
        self.assertEqual(2, len(self.parser.operands()))
        self.parser.__next__()
        self.assertEqual("OPRB", self.parser.mnemonic())
        self.assertEqual(10, self.parser.operands()[0].value)
        self.assertEqual(20, self.parser.operands()[1].value)
        self.assertEqual(2, len(self.parser.operands()))

    def test_raw(self):
        source = "_RAW >>+"
        self.parser.parse(source).__next__()
        self.assertEqual("_RAW", self.parser.mnemonic())
        self.assertEqual(1, self.parser.operand_count())
        self.assertEqual(Raw, type(self.parser.operands()[0]))
        self.assertEqual(">>+", self.parser.operands()[0].value)
