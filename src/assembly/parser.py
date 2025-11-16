import pyparsing as pp
from pyparsing import ParserElement, ParseResults


class Symbol:

    def __init__(self, parse_result):
        self._value = parse_result[0]['Value']
        self._bitwidth = parse_result[0]['Bitwidth']

    @property
    def value(self):
        return self._value

    @property
    def bitwidth(self):
        return self._bitwidth

    def __repr__(self):
        return f"{self._value}" + (f":{self._bitwidth}" if self._bitwidth != 8 else "")


class Immediate:

    def __init__(self, parse_result):
        self._value = parse_result[0]['Value']
        self._bitwidth = parse_result[0]['Bitwidth']

    @property
    def value(self):
        return self._value

    @property
    def bitwidth(self):
        return self._bitwidth

    def __repr__(self):
        return f"{self._value}" + (f":{self._bitwidth}" if self._bitwidth != 8 else "")


class Address:

    def __init__(self, parse_result):

        bases = parse_result[0]["Base"]
        indexes = parse_result[0]["Index"]

        self._base = next((bases[c] for c in ("Symbol", "Immediate") if bases.get(c) is not None))

        if "Base" in indexes:
            self._index = next((indexes["Base"][c] for c in ("Symbol", "Immediate") if indexes["Base"].get(c) is not None))
            self._indirect = True
        elif "Top" in indexes:
            self._index = indexes["Top"]
            self._indirect = True
        else:
            self._index = indexes["Immediate"]
            self._indirect = False

    def resolve_direct(self, vtable: dict):
        base = self.resolve_base(vtable)
        index = self.resolve_index(vtable)
        cell_jump = 4 if self.base.bitwidth == 16 else 1
        return base + (cell_jump * index)

    def resolve_base(self, vtable: dict) -> int:
        result = 0
        if isinstance(self._base, Symbol):
            result += vtable[self._base.value]
        else:
            result += self._base.value
        return result

    def resolve_index(self, vtable: dict) -> int:
        result = 0
        if isinstance(self._index, Immediate):
            result += self._index.value
        else:
            result += self._index.resolve_base(vtable)
        return result

    @property
    def indirect(self):
        return self._indirect

    @property
    def base(self):
        return self._base

    @property
    def index(self):
        return self._index

    def __repr__(self):
        return f"@{self._base}" + (
            f"[{'@' if Symbol == type(self._index) else ''}{self._index}]" if isinstance(self._index, Top) or self._index.value != 0 else "")


class Top:

    def __init__(self, parse_result):
        self._bitwidth = parse_result[0]['Bitwidth']

    @property
    def bitwidth(self):
        return self._bitwidth

    def __repr__(self):
        return f"@top" + (f":{self._bitwidth}" if self._bitwidth != 8 else "")

class Raw:

    def __init__(self, parse_result):
        self._value = ''.join(parse_result['Raw'].as_list())

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return self.value


class Parser:

    def __init__(self):
        self.lines = []
        self.index = 0
        self._current = None

    def parse(self, source: str):
        source = '\n'.join([s for s in source.splitlines() if len(s.strip()) > 0])
        ParserElement.set_default_whitespace_chars(' \t')
        bitwidth = pp.Combine(pp.Suppress(":") + pp.Word(pp.nums)) \
            .set_results_name("Bitwidth") \
            .set_parse_action(pp.common.convert_to_integer)
        immediate = pp.Combine(
            pp.Word(pp.nums)("Value").set_parse_action(pp.common.convert_to_integer) + pp.Opt(bitwidth, 8)) \
            .set_results_name("Immediate") \
            .set_parse_action(lambda orig, loc, result: Immediate(result))
        symbol = pp.Combine((~pp.Keyword("top") + pp.Word(pp.alphas)("Value")) + pp.Opt(bitwidth, 8)) \
            .set_results_name("Symbol") \
            .set_parse_action(lambda orig, loc, result: Symbol(result))
        top = pp.Combine(pp.Suppress("@") + pp.Keyword("top") + pp.Opt(bitwidth, 8))("Top") \
            .set_parse_action(lambda orig, loc, result: Top(result))
        base_address = pp.Combine(pp.Suppress("@") + (immediate ^ symbol))("Base")
        address = pp.Forward()
        index = pp.Combine(pp.Suppress('[') + (immediate ^ base_address ^ top) + pp.Suppress(']'))("Index")
        address <<= pp.Combine(base_address + pp.Opt(index, immediate.parse_string("0"))) \
            .set_results_name("Address") \
            .set_parse_action(lambda orig, loc, result: Address(result))
        raw = pp.Word("+-><[],.")[1,...]("Raw") \
            .leave_whitespace(False) \
            .set_parse_action(lambda orig, loc, result: Raw(result))
        operand = pp.Group(raw ^ immediate ^ symbol ^ address ^ top)
        operands = pp.ZeroOrMore(operand).set_results_name("Operands")
        mnemonic = pp.Word(pp.alphas + "_", exact=4)("Mnemonic")
        comment = ("#" + pp.rest_of_line)("Comment")
        instruction = pp.Group(comment ^ (mnemonic + operands + pp.Optional(comment)))
        program = (pp.OneOrMore(instruction + pp.Suppress(pp.LineEnd())))("Program")
        program.ignore(comment)
        program.set_debug(False)

        self.lines = program.parse_string(source, parse_all=True)
        self.index = 0

        return self

    def mnemonic(self) -> str:
        return self._current["Mnemonic"]

    def operand_count(self) -> int:
        return len(self._current["Operands"])

    def operands(self):
        return [self._current["Operands"][i].values().__next__() for i in range(self.operand_count())]

    def dump(self):
        return self._current.dump()

    def _combine_raw(self, original, location, parse_results):
        return parse_results

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.lines):
            self._current = self.lines[self.index]
            self.index += 1
            return self._current
        else:
            raise StopIteration
