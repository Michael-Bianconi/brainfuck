from typing import List

from pyparsing import ZeroOrMore, OneOrMore, Literal, Suppress, Or, FollowedBy, Forward, PrecededBy, ParseResults


class BrainfuckOptimizer:
    """
    This parser consumes Brainfuck source and produces Optimized Brainfuck (OBF) instructions.
    """

    @staticmethod
    def load_bfo(bfo: str) -> list:
        result = []
        for line in bfo.splitlines():
            line = line.strip()
            if line.isspace():
                continue
            try:
                operator, *args = line.split()
                args = list(map(int, args))
                result.append(OBFToken(operator, args))
            except ValueError:
                print(line)
        return result

    @staticmethod
    def run(source) -> list:

        program = Forward()

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
        mov = ((jfz + mdp('first') + Literal('+') + mdp('second') + Literal('-') + jbn) |
              (jfz + Literal('-') + mdp('first') + Literal('+') + mdp('second') + jbn)) \
            .add_condition(lambda t: t['first'].args[0] + t['second'].args[0] == 0) \
            .add_parse_action(lambda t: OBFToken('mov', [t['first'].args[0]]))

        # [->>>+>+<<<<]
        # [>>>+>+<<<<-]
        # [-<<+>+>]
        mmv = ((jfz + mdp('first') + Literal('+') + mdp('second') + Literal('+') + mdp('third') + Literal('-') + jbn) |
              (jfz + Literal('-') + mdp('first') + Literal('+') + mdp('second') + Literal('+') + mdp('third') + jbn)) \
            .add_condition(lambda t: sum([t['first'].args[0], t['second'].args[0], t['third'].args[0]]) == 0) \
            .add_parse_action(lambda t: OBFToken('mmv', [t['first'].args[0], t['first'].args[0] + t['second'].args[0]]))

        cpy = (mdp + res + mdp + mmv + mdp + mov + mdp) \
            .add_condition(lambda t: t[0].args[0] == -t[2].args[0] == t[3].args[1] == t[4].args[0] == -t[5].args[0] == -t[6].args[0]) \
            .add_parse_action(lambda t: OBFToken('cpy', t[3].args))

        program <<= ZeroOrMore(cpy | mmv | mov | res | mdp | inc | jfz | jbn | dbg)

        result = program.parse_string(source).as_list()
        BrainfuckOptimizer.resolve_jumps(result)

        return result

    @staticmethod
    def resolve_jumps(program):
        for i in range(len(program)):
            if program[i].operator == "jfz":
                counter = 0
                for j in range(i, len(program)):
                    if program[j].operator == "jfz":
                        counter += 1
                    elif program[j].operator == "jbn":
                        counter -= 1
                    if counter == 0:
                        program[i].args = [j-i]
                        program[j].args = [j-i]
                        break



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

