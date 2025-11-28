import pyparsing as pp
from pyparsing import ParserElement, ParseResults


class Operand:
    """
    Operand Types:

    Immediate: An integer value (e.g. 5)
    Symbol: A string that does not start with a number, which will be associated with an address in memory
    Address: A location in memory, either immediate (@6) or symbolic (@a)
    Top: A special symbol denoting the top of the stack
    Raw: Proper brainfuck code (symbols include +-[],.<>)

    Note:
        The @ in "@a" means "use the value at address a". This is in contrast to just "a", which means
        "treat a as an immediate equal to the address itself".

        Example (assume a is associated with address 20, and memory[20] = 100):
            PUSH @top @a        # Push 100 onto the stack
            PUSH @top &a        # Push 20 onto the stack
            PUSH @top a         # ERROR unexpected Symbol
    """

    def __init__(self, parse_result, value_type):
        if value_type == "Raw":
            self._value = ''.join(parse_result['Raw'].as_list())
        else:
            self._value = parse_result[0]
        self._value_type = value_type

    def resolve(self, vtable):

        # Addresses may be @0 or @a
        if self._value_type == "Address":
            try:
                return int(self._value)
            except ValueError:
                return vtable[self._value]

        # Immediates may be 5 or &a
        elif self._value_type == "Immediate":
            if self._value.startswith("&"):
                return vtable[self._value[1:]]
            else:
                return int(self._value)

        else:
            return self._value

    @property
    def value_type(self):
        return self._value_type

    def __repr__(self):
        return f"{self._value}"


class Parser:

    def __init__(self):
        self.lines = []
        self.index = 0
        self._current = None

    def parse(self, source: str):
        source = '\n'.join([s for s in source.splitlines() if len(s.strip()) > 0])
        ParserElement.set_default_whitespace_chars(' \t')
        immediate = pp.Combine(
            (pp.Opt(pp.Literal('-')) + pp.Word(pp.nums))
            .set_parse_action(lambda o, l, r: int(''.join(r.as_list())))) \
            .set_parse_action(lambda orig, loc, result: Operand(result, "Immediate"))
        address_of = pp.Combine(pp.Literal("&") + ~pp.Keyword("top") + pp.Word(pp.alphas)) \
            .set_parse_action(lambda orig, loc, result: Operand(result, "Immediate"))
        symbol = pp.Combine(~pp.Keyword("top") + pp.common.identifier) \
            .set_parse_action(lambda orig, loc, result: Operand(result, "Symbol"))
        top = pp.Combine(pp.Suppress("@") + pp.Keyword("top"))("Top") \
            .set_parse_action(lambda orig, loc, result: Operand(result, "Top"))
        address = pp.Combine(pp.Suppress("@") + (immediate ^ symbol)) \
            .set_parse_action(lambda orig, loc, result: Operand(result, "Address"))
        raw = pp.Word("+-><[],.")[1,...]("Raw") \
            .leave_whitespace(False) \
            .set_parse_action(lambda orig, loc, result: Operand(result, "Raw"))
        operands = pp.ZeroOrMore(pp.Group(raw ^ immediate ^ symbol ^ address ^ address_of ^ top)) \
            .set_results_name("Operands")
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
