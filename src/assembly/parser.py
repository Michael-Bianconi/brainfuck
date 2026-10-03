import pyparsing as pp
from pyparsing import ParserElement


class Operand:

    def __init__(self, operand_type, operand_value):
        self.operand_type = operand_type
        self.operand_value = operand_value

    def __repr__(self):
        return f"{self.operand_value}"


class Immediate(Operand):

    def __init__(self, value):
        super().__init__("immediate", int(value[0]))
        self.value = value


class Label(Operand):

    def __init__(self, symbol):
        super().__init__("label", symbol[0])


class ProgramCounter(Operand):

    def __init__(self):
        super().__init__("$pc", "$pc")


class StackPointer(Operand):

    def __init__(self):
        super().__init__("$sp", "$sp")


class Register(Operand):

    positions = {
        "$c0": 0,
        "$c1": 1,
        "$v0": 2,
        "$v1": 3
    }

    def __init__(self, mnemonic):
        super().__init__("register", self)
        self._mnemonic = mnemonic[0]

    def mnemonic(self):
        return self._mnemonic

    def ordinal(self):
        return self.positions[self._mnemonic]

    def address(self):
        return self.ordinal() * 2


class Native(Operand):

    def __init__(self, native):
        super().__init__("native", native[0])


class Parser:

    def __init__(self):
        self.lines = []
        self.index = 0
        self._current = None

    def parse(self, source: str):
        source = '\n'.join([s for s in source.splitlines() if len(s.strip()) > 0])
        ParserElement.set_default_whitespace_chars(' \t')

        immediate = pp.Combine(pp.Optional(pp.Literal("-")) + pp.Word(pp.nums)).set_parse_action(lambda o, l, result: Immediate(result))
        label = pp.Word(pp.alphanums).set_parse_action(lambda o, l, result: Label(result))
        register = pp.oneOf(["$c0", "$c1", "$v0", "$v1"]).set_parse_action(lambda o, l, result: Register(result))
        sp = pp.Keyword("$sp").set_parse_action(lambda o, l, r: StackPointer())
        pc = pp.Keyword("$pc").set_parse_action(lambda o, l, r: ProgramCounter())
        native = pp.Word("+-[]<>.,").set_parse_action(lambda o, l, result: Native(result))
        operands = pp.ZeroOrMore(pp.Group(immediate ^ label ^ register ^ native ^ sp ^ pc)).set_results_name("Operands")

        mnemonic = pp.Combine(pp.Word(pp.alphas + "_", exact=4) +
                              pp.ZeroOrMore(pp.Combine(pp.Literal(":") + pp.Word(pp.nums))))("Mnemonic")
        comment = ("#" + pp.rest_of_line)("Comment")
        instruction = pp.Group(mnemonic + operands + pp.LineEnd())

        program = pp.ZeroOrMore(instruction ^ pp.Suppress(pp.LineEnd()))("Program")

        program.ignore(comment)
        program.set_debug(False)

        self.lines = program.parse_string(source, parse_all=True)
        self.index = 0

        return self

    def mnemonic(self) -> str:
        parts = self._current["Mnemonic"].split(":")
        name = parts[0]
        bitwidths = parts[1:]

        # 1. No params → return name
        if not bitwidths:
            return name

        # 2. All params are "8" → return name
        if all(p == "8" for p in bitwidths):
            return name

        # 3. All params are "16" → return name:16
        if all(p == "16" for p in bitwidths):
            return f"{name}:16"

        # 4. Otherwise → original string
        return self._current["Mnemonic"]

    def operand_count(self) -> int:
        return len(self._current["Operands"])

    def operands(self):
        return [o[0] for o in self._current["Operands"]]

    def dump(self):
        return self._current.dump()

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.lines):
            self._current = self.lines[self.index]
            self.index += 1
            return self._current
        else:
            raise StopIteration
