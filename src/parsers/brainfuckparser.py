from pyparsing import ZeroOrMore, OneOrMore, Literal, Suppress, Or


class BrainfuckParser:
    """
    This parser consumes Brainfuck source and produces Optimized Brainfuck (OBF) instructions.
    """

    @staticmethod
    def run(source):

        mdp = (OneOrMore(Literal(">")) | OneOrMore(Literal("<"))) \
            .set_parse_action(lambda t: OBFToken("mdp", [len(t) * (1 if t[0] == ">" else -1)]))

        inc = (OneOrMore(Literal("+")) | OneOrMore(Literal("-"))) \
            .set_parse_action(lambda t: OBFToken("inc", [len(t) * (1 if t[0] == "+" else -1)]))

        jfz = Literal('[').set_parse_action(lambda t: OBFToken('jfz', []))
        jbn = Literal(']').set_parse_action(lambda t: OBFToken('jbn', []))
        dbg = Literal('#').set_parse_action(lambda t: OBFToken('dbg', []))
        res = Literal('[-]').set_parse_action(lambda t: OBFToken('res', []))

        # Matches on a conventional _MOV instruction, such as:
        # 1. [>>>+<<<-]
        # 2. [<<+>>-]
        # 3. [->>>+<<<]
        mov = ((jfz + mdp('first') + Literal('+') + mdp('second') + Literal('-') + jbn) | \
              (jfz + Literal('-') + mdp('first') + Literal('+') + mdp('second') + jbn)) \
            .add_condition(lambda t: t['first'].args[0] + t['second'].args[0] == 0) \
            .add_parse_action(lambda t: OBFToken('mov', [t['first'].args[0]]))

        # [->>>+>+<<<<]
        # [>>>+>+<<<<-]
        # [-<<+>+>]
        mmv = ((jfz + mdp('first') + Literal('+') + mdp('second') + Literal('+') + mdp('third') + Literal('-') + jbn) | \
              (jfz + Literal('-') + mdp('first') + Literal('+') + mdp('second') + Literal('+') + mdp('third') + jbn)) \
            .add_condition(lambda t: sum([t['first'].args[0], t['second'].args[0], t['third'].args[0]]) == 0) \
            .add_parse_action(lambda t: OBFToken('mmv', [t['first'].args[0], t['second'].args[0]]))

        program = ZeroOrMore(mmv | mov | res | mdp | inc | jfz | jbn | dbg)

        return program.parse_string(source).as_list()


class OBFToken:

    def __init__(self, operator: str, args: list):
        self.operator = operator
        self.args = args

    def __repr__(self):
        return self.operator + ' ' + ' '.join([str(a) for a in self.args])

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, OBFToken):
            return False
        else:
            return self.operator == other.operator and self.args == other.args

