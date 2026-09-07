import sys

from src.parsers.bfparser import BrainfuckParser


class OptimizedInterpreter:

    def __init__(self, memsize=30000):
        self.source = []
        self.instruction_count = 0
        self.memory = [0 for _ in range(memsize)]
        self.dptr = 0
        self.iptr = 0
        self.openbrackets = {}
        self.closebrackets = {}
        self.cycles = 0

    def run(self, source, debug=False):
        self.source = BrainfuckParser.run(source)
        self.instruction_count = len(self.source)

        try:
            while self.iptr < self.instruction_count:
                op = self.source[self.iptr]
                if op.operator == 'jfz':
                    if self.memory[self.dptr] == 0:
                        self._jump()
                elif op.operator == 'jbn':
                    if self.memory[self.dptr] != 0:
                        self._jump()
                elif op.operator == 'inc':
                    self.memory[self.dptr] = (self.memory[self.dptr] + op.args[0]) % 256
                elif op.operator == 'mdp':
                    self.dptr += op.args[0]
                elif op.operator == 'res':
                    self.memory[self.dptr] = 0
                elif op.operator == 'mov':
                    self.memory[self.dptr + op.args[0]] += self.memory[self.dptr]
                    self.memory[self.dptr] = 0
                elif op.operator == 'mmv':
                    self.memory[self.dptr + op.args[0]] += self.memory[self.dptr]
                    self.memory[self.dptr + op.args[0] + op.args[1]] += self.memory[self.dptr]
                    self.memory[self.dptr] = 0
                elif op.operator == '.':
                    print(chr(self.memory[self.dptr]), flush=True, end='')
                elif op.operator == ',':
                    self.memory[self.dptr] = ord(sys.stdin.read(1))
                elif op.operator == 'dbg':
                    debug = not debug
                elif op.operator == "H":
                    break

                if debug:
                    tape_start = max(0, self.dptr - 12)
                    dump_dptr = min(12, self.dptr)
                    mem_dump = list(' ' + ' '.join(['{:02x}'.format(i) for i in self.memory[tape_start:tape_start+20]]) + ' ')
                    mem_dump[3 * dump_dptr] = '('
                    mem_dump[3 * (dump_dptr+1)] = ')'
                    mem_dump = ''.join(mem_dump)

                    print(f"DEBUG: i=[{'{:5d}'.format(self.iptr)}] d=[{'{:5d}'.format(self.dptr)}] op=[{op.__repr__()}] {mem_dump}")

                self.iptr += 1
                self.cycles += 1
            print('\n')
        except IndexError as e:
            print(f"ERROR DUMP i=[{'{:4d}'.format(self.iptr)}] d=[{'{:4d}'.format(self.dptr)}]")
            raise e

    def _jump(self):
        direction = 1 if self.source[self.iptr].operator == 'jfz' else -1
        bracketcounter = direction
        self.iptr += direction

        while bracketcounter != 0:
            if self.source[self.iptr].operator == 'jfz':
                bracketcounter += 1
            elif self.source[self.iptr].operator == 'jbn':
                bracketcounter -= 1

            self.iptr += direction

        self.iptr -= direction
