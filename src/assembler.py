class Assembler:
    """
    Bitwidth:

    Each memory cell holds a single byte (bitwidth 8). To enable 16-bit or 32-bit, additional memory cell
    must be used. Unfortunately, these larger bitwidths require additional temporary memory cells.
    """

    def __init__(self):
        self.vtable = {}
        self.stack_pointer = 0

    def right(self, i: int, bitwidth=8):
        """
        Moves data pointer right by immediate value.
        :param i: The immediate value to move by.
        :param bitwidth: 8-bit (1 cell) by default. May be 8, 16, 24, or 32.
        :return:
        """
        if bitwidth == 8:
            return '>' * i
        elif bitwidth == 16:
            return '>>>>' * i

    def left(self, i: int, bitwidth=8):
        if bitwidth == 8:
            return '<' * i
        elif bitwidth == 16:
            return '<<<<' * i
    
    def add(self, i, bitwidth=8):
        """
        Increments the current value by the given value. Expects overflow behavior from the interpreter.

        If bitwidth is 8, only modifies the current memory cell.

        If bitwidth is 16, expects memory to be laid out as [low, high, carry, temp], where
        1. low contains the lowest 8 bits of the 16-bit value
        2. high contains the upper 8 bits of the 16-bit value
        3. carry is set to 0
        4. temp is set to 0
        5. The data pointer is pointing at low

        Calling this method with a large i will enable certain optimizations not available
        if a small i is used many times.

        :param i: The amount to increment the current value by.
        :param bitwidth: 8|16
        :return:
        """
        if bitwidth == 8:                   # [x] data pointer at x
            return '+' * (i % 256)
        elif bitwidth == 16:                # [low, high, carry, temp] data pointer at x
            result = ''
            high_add = i // 256
            low_add = i % 256

            # Save potentially billions of cycles (for very large i) by modifying the high bits directly,
            # adding 256 to the total value each time. This block can be omitted entirely by repeating the +1
            # block by the full value of i.
            if high_add > 0:
                result += f">{self.add(high_add, bitwidth=8)}<"

            # Add +1 to the low bits. If that causes an overflow, increment the high bits by +1.
            # Repeat this +1 process as many times as need.
            result += ''.join([             # If low+1 == 0       |   If low+1 != 0
                '+',                        # [0, high, 0, 0]      |   [low+1, high, 0, 0]      d=low
                '[>>+>+<<<-]'               # [0, high, 0, 0]      |   [0, high, low+1, low+1]  d=low
                '>>[<<+>>-]+>',             # [0, high, 1, 0]      |   [low+1, high, 1, low+1]  d=temp
                '[<->[-]]<',                # [0, high, 1, 0]      |   [low+1, high, 0, 0]      d=carry
                '[-<+>]<<'                  # [0, high+1, 0, 0]    |   [low+1, high, 0, 0]      d=low
            ]) * low_add

            return result
    
    def sub(self, i, bitwidth=8):
        if bitwidth == 8:
            return '-' * i
        elif bitwidth == 16:                # [x, y, c, t] data pointer at x
            high_sub = i // 256
            low_sub = i % 256
            result = ''
            # Save potentially billions of cycles (for very large i) by modifying the high bits directly,
            # adding 256 to the total value each time. This block can be omitted entirely by repeating the +1
            # block by the full value of i.
            if high_sub > 0:
                result += f">{self.sub(high_sub, bitwidth=8)}<"
            result += ''.join([                # If x == 0         |   If x != 0           d=x
                '[>>+>+<<<-]>>',            # [0, y, x, x]      |   [x, y, 0, 0]        d=c
                '[<<+>>-]+>',               # [x, y, 1, x]      |   [x, y, x, x]        d=t
                '[<->[-]]<',                # [x, y, 0, 0]      |   [x, y, 1, 0]        d=c
                '[-<->]<<-'                 # [x-1, y, 0, 0]    |   [255, y-1, 0, 0]    d=x
            ]) * low_sub
            return result

    def setzero(self, bitwidth=8):
        if bitwidth == 8:
            return '[-]'
        elif bitwidth == 16:
            return '[-]>[-]<'

    def load(self, i, bitwidth=8):
        """
        Loads immediate value on to the top of the stack. Increments stack pointer.
        :param i:
        :return:
        """
        if bitwidth == 8:
            self.stack_pointer += 1
            return ''.join([
                self.add(i),
                self.right(1)
            ])
        elif bitwidth == 16:
            self.stack_pointer += 4
            return ''.join([
                self.add(i, bitwidth=16),
                self.right(1, bitwidth=16)
            ])

    def aloc(self, v, i, bitwidth=8):
        """
        Allocates space for a variable on the stack. Stores variable name in vtable.
        Moves stack pointer to next position.
        :param v: Address lael
        :param x: Value to store in the allocated memory
        :return:
        """
        self.vtable[v] = self.stack_pointer

        if bitwidth == 8:
            self.stack_pointer += i
        elif bitwidth == 16:
            self.stack_pointer += i * 4
        return self.right(i, bitwidth=bitwidth)

    def push(self, a, bitwidth=8):
        """
        Copies the value at address a to the top of the stack.
        :param a:
        :return:
        """
        offset = self.stack_pointer - a
        if bitwidth == 8:
            self.stack_pointer += 1
            return ''.join([
                self.left(offset),
                '[',
                self.sub(1),
                self.right(offset),
                self.add(1),
                self.right(1),
                self.add(1),
                self.left(offset + 1),
                ']',
                self.right(offset + 1),
                '[',
                self.sub(1),
                self.left(offset + 1),
                self.add(1),
                self.right(offset + 1),
                ']'
            ])
        elif bitwidth == 16:
            return ''.join([
                self.push(a, bitwidth=8),
                self.push(a+1, bitwidth=8),
                self.load(0),
                self.load(0)
            ])

    def setvar(self, a, x, bitwidth=8):
        return ''.join([
            self.left(self.stack_pointer - a),
            self.setzero(bitwidth=bitwidth),
            self.add(x, bitwidth=bitwidth),
            self.right(self.stack_pointer - a)
        ])

    def pop(self, bitwidth=8):
        if bitwidth == 8:
            self.stack_pointer -= 1
            return '<[-]'
        elif bitwidth == 16:
            self.stack_pointer -= 4
            return '<<<[-]<[-]'

    def plus(self, a_bits, b_bits, out_bits):
        """
        Input:  [... a b | 0]
        Output: [... a+b | 0 0]

        Pops b off the stack. Pops a off the stack. Pushes the sum of a+b to the stack.

        :param a_bits: 8|16 The size of the a value.
        :param b_bits: 8|16 The size of the b value.
        :param out_bits: 8|16 The size of the sum value.
        :return:
        """
        if a_bits == 8 and b_bits == 8 and out_bits == 8:
            return self.plus_8_8_8()
        elif a_bits == 16 and b_bits == 16 and out_bits == 16:
            return self.plus_16_16_16()

    def plus_8_8_8(self):
        """
        Input:  [... a b | 0]
        Output: [... c | 0 0]

        Pops b off the stack. Pops a off the stack. Pushes the sum of (a+b) % 256 to the stack.
        """
        self.stack_pointer -= 1
        return '<[<+>-]'

    def plus_16_16_16(self):
        """
        Input:  [... a a 0 0 b b 0 0 | 0]
        Output: [... c c 0 0 | 0 0 0 0 0]

        Pops b off the stack. Pops a off the stack. Pushes the sum of (a+b) % 256 to the stack.
        """
        self.stack_pointer -= 4
        return ''.join([
            self.left(1, bitwidth=16),
            '>[<',  # While y high bits are nonzero
            self.left(1, bitwidth=16),
            self.add(256, bitwidth=16),
            self.right(1, bitwidth=16),
            self.sub(256, bitwidth=16),
            '>]<[',
            self.left(1, bitwidth=16),
            self.add(1, bitwidth=16),
            self.right(1, bitwidth=16),
            self.sub(1, bitwidth=16),
            ']'
        ])

    def minus(self, bitwidth=8):
        """
        Pops the top two values off the stack. Subtracts the second from the first.
        Pushes the result to the stack.

        :return:
        """
        if bitwidth == 8:
            self.stack_pointer -= 1
            return '<[<->-]'
        elif bitwidth == 16:
            self.stack_pointer -= 4
            return ''.join([
                self.left(1, bitwidth=16),
                '>[<',                          # While y high bits are nonzero
                self.left(1, bitwidth=16),   #      Move to x
                self.sub(256, bitwidth=16),  #      Add 256 to x
                self.right(1, bitwidth=16),  #      Move to y
                self.sub(256, bitwidth=16),  #      Subtract 256 from y
                '>]<[',                         # End while. While y low bits are nonzero
                self.left(1, bitwidth=16),
                self.sub(1, bitwidth=16),
                self.right(1, bitwidth=16),
                self.sub(1, bitwidth=16),
                ']'
            ])

    def is_nonzero(self, bitwidth=8):
        if bitwidth == 8:
            return ''.join([
                '+<[[-]+>-]>',      # [0, 1<, 0]   | [1, 0, 0<]
                '[->]<<'            # [0<, 0, 0]   | [1<, 0, 0]
            ])

    def is_zero(self, bitwidth=8):
        """
        Pops the top value off the stack. If it's zero, pushes an 8-bit 1 onto the stack.
        If it's nonzero, pushes an 8-bit zero onto the stack.
        :param bitwidth:
        :return:
        """
        if bitwidth == 8:           # [n, 0<, 0]
            return ''.join([        # If n is zero      | If n is nonzero
                '+<[>-]>',          # [0, 1<, 0]        | [n, 0, 0<]
                '[<+>->]<<'         # [1<, 0, 0]        |
            ])

    def logical_and(self, bitwidth=8):
        """
        Pops the top two values off the stack. If both are non-zero, pushes 1 onto the stack. Otherwise, pushes 0.
        :param bitwidth:
        :return:
        """
        if bitwidth == 8:
            self.stack_pointer -= 1
            return ''.join([                    # [0, 0 | 0]        [n, 0 | 0]      [0, y | 0]      [x, y | 0]
                '<<[>>+<<[-]]'                  # [| 0, 0, 0]       [| 0, 0, 1]     [| 0, y, 0]     [| 0, y, 1]
                '>[>+<[-]]>',                   # [0, 0 | 0]        [0, 0 | 1]      [0, 0 | 1]      [0, 0 | 2]
                '[-[<<+>>[-]]]<'                 # [0 | 0, 0]        [0 | 0, 0]      [0 | 0, 0]      [1 | 0, 0]
            ])

    def equals(self, bitwidth=8):
        """
        Pops the top two values off the stack. If they are the same, pushes 1 onto the stack.
        If they are not the same, pushes 0 onto the stack.
        :return:
        """
        if bitwidth == 8:                           # [x, y] d=y
            return ''.join([                        # If x == y      | If x != y
                self.minus(bitwidth=bitwidth),      # [0, 0]         | [z, 0]     d=y
                '+<',                               # [0, 1]         | [z, 1]     d=x
                '[[-]>-<]>',                        # [0, 1]         | [0, 0]     d=y
                '[<+>-]'                            # [1, 0]         | [0, 0]     d=y
            ])
        elif bitwidth == 16:                        # [x1, x2, 0, 0, y1, y2, 0, 0 | 0, 0, 0, 0]
            x1 = self.stack_pointer - 8
            x2 = self.stack_pointer - 7
            y1 = self.stack_pointer - 4
            y2 = self.stack_pointer - 3
            source = ''.join([
                self.push(x1, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1 | 0, 0, 0]
                self.push(y1, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1, y1 | 0, 0]
                self.equals(bitwidth=8),            # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1 | 0, 0, 0]
                self.push(x2, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1, x2 | 0, 0]
                self.push(y2, bitwidth=8),          # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1, x2, y2 | 0]
                self.equals(bitwidth=8),            # [x1, x2, 0, 0, y1, y2, 0, 0, x1==y1, x2==y2 | 0, 0]
                self.logical_and(bitwidth=8),       # [x1, x2, 0, 0, y1, y2, 0, 0, x==y | 0, 0, 0]
                '<<<<[-]<[-]<<<[-]<[-]>>>>>>>>',    # [0, 0, 0, 0, 0, 0, 0, 0 | x==y, 0, 0, 0]
                '[<<<<<<<<+>>>>>>>>-]<<<<<<<',      # [x==y | 0]
            ])
            self.stack_pointer -= 8
            return source


    def logical_not(self):
        """
        Pops the top value from the stack. If it is non-zero, pushes 0. If it is 0, pushes 1.
        :return:
        """
        return ''.join([        # [x, 0]
            self.load(0),       # [x, 0, 0]
            self.equals()       # If zero, [1, 0]. If nonzero, [0, 0]
        ])

    def if_nonzero(self):
        """
        Starts an if-statement. Peeks at top value on the stack. If it is non-zero, enters
        the inner code block. If zero, skips code block. Must be paired with an end_if().

        If-statement inner code block must:
            * Have a stack-effect of 0.
            * Must not modify the top value on the stack.

        :return:
        """
        return ''.join([            # [x, y, 0]
            '<[>'                   # If equal, enter inner code block.
        ])

    def if_zero(self):
        return ''.join([
            self.logical_not(),
            self.if_nonzero()
        ])

    def end_if(self):
        """
        Ends the enclosing if-statement. Pops the if-condition off the stack.
        :return:
        """
        return ''.join([
            ']',
            self.pop()
        ])

    def swap(self, bitwidth=8):
        """
        Pops b off the stack. Pops a off the stack. Pushes b onto the stack. Pushes a onto the stack.
        :param bitwidth:
        :return:
        """
        if bitwidth == 8:
            return ''.join([                    # [a, b | 0]
                '<[>+<-]',                      # [a | 0, b]
                '<[>+<-]>>',                    # [0, a | b]
                '[<<+>>-]'                      # [b, a | 0]
            ])

    def get_indirect(self, a, bitwidth=8):
        """
        Pops an address off the stack. Pushes the value at that address onto the stack.

        :param a: The address of the first cell in the array of cells. Set to 0 for absolute address.
        :param bitwidth:
        :return: Pushes a[i] onto the stack.
        """
        if bitwidth == 8:
            return ''.join([                                # [a ... x ... i | 0]
                self.load(0, bitwidth=8),                 # [a ... x ... i 0 | 0]
                self.swap(bitwidth=8),                      # [a ... x ... 0 i | 0]
                '<[[>]+[<]>-]>[>]',                        # [a ... x ... 0 0 1 ... 1 1 | 0]
                self.push(a, bitwidth=8),                   # [a ... x ... 0 0 1 ... 1 1 | x]
                '<<[->[<+>-]<<]>>',                         # [a ... x ... 0 0 x | 0]
                self.swap(bitwidth=8),
                self.pop(bitwidth=8),
                self.swap(bitwidth=8),
                self.pop(bitwidth=8)                        # [a ... x ... x | 0]
            ])

    def set_indirect(self, a, bitwidth=8):
        """
        Pops the top value off the stack as the index (a[x]).
        Pops the next value off the stack as the value (y).
        Sets a[x] = y.
        :param a:
        :param bitwidth:
        :return:
        """
        if bitwidth == 8:
            return ''


