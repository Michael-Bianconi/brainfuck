import sys
class Interpreter:

    def __init__(self, source, memsize=30000):
        self.source = source
        self.memory = [0 for _ in range(memsize)]
        self.dptr = 0
        self.iptr = 0
    def run(self):
        self.dptr = 0
        self.iptr = 0
        while self.iptr < len(self.source):
            op = self.source[self.iptr]
            if op == '[':
                if self.memory[self.dptr] == 0:
                    self._jump()
            elif op == ']':
                if self.memory[self.dptr] != 0:
                    self._jump()
            elif op == '+':
                self.memory[self.dptr] = (self.memory[self.dptr] + 1) % 255
            elif op == '-':
                self.memory[self.dptr] = (self.memory[self.dptr] - 1) % 255
            elif op == '>':
                self.dptr += 1
            elif op == '<':
                self.dptr -= 1
            elif op == '.':
                print(chr(self.memory[self.dptr]), flush=True, end='')
            elif op == ',':
                self.memory[self.dptr] = ord(sys.stdin.read(1))
            self.iptr += 1
        print('\n')

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