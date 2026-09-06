import sys


class Interpreter:

    def __init__(self, memsize=30000):
        self.source = ""
        self.memory = [0 for _ in range(memsize)]
        self.dptr = 0
        self.iptr = 0
        self.openbrackets = {}
        self.closebrackets = {}
        self.cycles = 0


    def run(self, source, debug=False):
        self.source = source
        try:
            while self.iptr < len(self.source):
                op = self.source[self.iptr]
                if op == '[':
                    if self.memory[self.dptr] == 0:
                        self._jump()
                elif op == ']':
                    if self.memory[self.dptr] != 0:
                        self._jump()
                elif op == '+':
                    self.memory[self.dptr] = (self.memory[self.dptr] + 1) % 256
                elif op == '-':
                    self.memory[self.dptr] = (self.memory[self.dptr] - 1) % 256
                elif op == '>':
                    self.dptr += 1
                elif op == '<':
                    self.dptr -= 1
                elif op == '.':
                    print(chr(self.memory[self.dptr]), flush=True, end='')
                elif op == ',':
                    self.memory[self.dptr] = ord(sys.stdin.read(1))
                elif op == '#':
                    debug = not debug
                elif op == "H":
                    break

                if debug:
                    tape_start = max(0, self.dptr - 12)
                    dump_dptr = min(12, self.dptr)
                    mem_dump = list(' ' + ' '.join(['{:02x}'.format(i) for i in self.memory[tape_start:tape_start+20]]) + ' ')
                    mem_dump[3 * dump_dptr] = '('
                    mem_dump[3 * (dump_dptr+1)] = ')'
                    mem_dump = ''.join(mem_dump)

                    print(f"DEBUG: i=[{'{:5d}'.format(self.iptr)}] d=[{'{:5d}'.format(self.dptr)}] op=[{op}] {mem_dump}")

                self.iptr += 1
                self.cycles += 1
            print('\n')
        except IndexError as e:
            print(f"ERROR DUMP i=[{'{:4d}'.format(self.iptr)}] d=[{'{:4d}'.format(self.dptr)}]")
            raise e

    def _jump(self):
        direction = 1 if self.source[self.iptr] == '[' else -1
        bracketcounter = direction
        self.iptr += direction

        while bracketcounter != 0:
            if self.source[self.iptr] == '[':
                bracketcounter += 1
            elif self.source[self.iptr] == ']':
                bracketcounter -= 1

            self.iptr += direction

        self.iptr -= direction

