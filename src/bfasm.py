from enum import Enum

IMMEDIATE = 'I'
REGISTER = 'R'
STRING = 'S'
VARNAME = 'V'
ARRAY = 'A'
ADDRESS = '$'

ZEROCELL = 7


class Instruction:

    def __init__(self, mnemonic, op1, op2, func):
        self.mnemonic = mnemonic
        self.op1 = op1
        self.op2 = op2
        self.func = func

    def __str__(self):
        return self.mnemonic

    def __repr__(self):
        return f"{self.mnemonic} {self.op1} {self.op2}"


class InternalInstruction(Instruction):
    pass


class PseudoInstruction(Instruction):
    pass


class AllocatedMemory:

    def __init__(self, cell, length):
        self.cell = cell
        self.length = length


class State:

    def __init__(self, stackaddr=255):
        self.nextdatacell = 0
        self.stackpointer = stackaddr
        self.currentblock = None
        self.data = {}
        self.blocks = {}
        self.opmap = {

            # Internal Instructions
            '_MOV': InternalInstruction('_MOV', IMMEDIATE, None, self.mov),  # Move data pointer
            '_ADD': InternalInstruction('_ADD', IMMEDIATE, None, self.add),  # Increment data pointer
            '_SUB': InternalInstruction('_SUB', IMMEDIATE, None, self.sub),  # Decrement data pointer
            '_LIN': InternalInstruction('_LIN', IMMEDIATE, None, self.lin),  # Load bytes from stdin into memory
            '_OUT': InternalInstruction('_OUT', IMMEDIATE, None, self.out),  # Print out bytes to stdout from memory
            '_RES': InternalInstruction('_RES', None, None, self.res),  # Set current memory cell to 0
            '_JFZ': InternalInstruction('_JFZ', None, None, self.jfz),  # Jump forward if current cell is zero
            '_JBN': InternalInstruction('_JBN', None, None, self.jbn),  # Jump backward if current cell is nonzero

            # Assembler Instructions
            'BLOC': PseudoInstruction('.BLOCK', VARNAME, None, None),  # Define a code block as a variable
            'EBLC': PseudoInstruction('.ENDBLOCK', IMMEDIATE, None, None),  # Ends code block

            # Heap/Stack
            'ALOC': PseudoInstruction('ALOC', VARNAME, IMMEDIATE, self.aloc),  # Allocate chunk of heap for variable
            'PUSH': PseudoInstruction('PUSH', ADDRESS, None, self.push),  # Push byte at address onto the stack
            'STOR': PseudoInstruction('STOR', IMMEDIATE, None, self.stor),  # Push immediate value onto the stack
            'POPS': PseudoInstruction('POPS', ADDRESS, None, self.pops),  # Pop stack into address
            'POPN': PseudoInstruction('POPN', None, None, self.popn),  # Pop stack and throw away value

            # Arithmetic
            'ADDI': PseudoInstruction('ADDI', ADDRESS, IMMEDIATE, self.addi),  # Increment variable by immediate
            'ADDA': PseudoInstruction('ADDA', ADDRESS, ADDRESS, self.adda),  # Increment variable by another variable
            'SETI': PseudoInstruction('SETI', ADDRESS, IMMEDIATE, self.seti),  # Set variable to immediate
            'COPY': PseudoInstruction('COPY', ADDRESS, ADDRESS, self.copy),  # Set variable to other variable
            'SUBI': PseudoInstruction('SUBI', ADDRESS, IMMEDIATE, self.subi),  # Decrement variable by immediate
            'SUBR': PseudoInstruction('SUBR', ADDRESS, ADDRESS, self.subr),  # Decrement variable by another variable
            'MULT': PseudoInstruction('MULT', ADDRESS, IMMEDIATE, self.mult),  # Multiply cell by x

            # Boolean logic
            'LNOT': PseudoInstruction('LNOT', ADDRESS, None, self.lnot),  # Logical not, sets n 1 if zero and 0 otherwise

            # Logic Flow
            'JINZ': PseudoInstruction('JINZ', ADDRESS, VARNAME, self.jinz),  # Executes the code block if n is nonzero
            'JIEZ': PseudoInstruction('JIEZ', ADDRESS, VARNAME, self.jiez),  # Executes the code block if n is zero

            # I/O
            'OUTC': PseudoInstruction('OUTI', ADDRESS, IMMEDIATE, self.outc)  # Prints bytes at address to stdout
        }

    def getaddress(self, varname):
        if varname not in self.data:
            raise Exception(f"{varname} not defined")
        else:
            return self.data[varname]

    def assemble(self, string):
        retval = ''
        lines = string.split('\n')
        for line in lines:
            line = line.split('#')[0].strip()
            if line == '':
                continue
            tokens = line.split()
            mnemonic = tokens[0].upper()
            op1 = tokens[1] if len(tokens) > 1 else None
            op2 = tokens[2] if len(tokens) > 2 else None
            instruction = self.opmap[mnemonic]
            if instruction.op1 == IMMEDIATE:
                op1 = int(op1)
            elif instruction.op1 == ADDRESS:
                if op1.isdigit():
                    op1 = int(op1)
                else:
                    op1 = self.getaddress(op1)
            if instruction.op2 == IMMEDIATE:
                op2 = int(op2)
            elif instruction.op2 == ADDRESS:
                if op2.isdigit():
                    op2 = int(op2)
                else:
                    op2 = self.getaddress(op2)
            if op1 is None and op2 is None:
                retval += self.opmap[mnemonic].func()
            elif op1 is not None and op2 is None:
                retval += self.opmap[mnemonic].func(op1)
            else:
                retval += self.opmap[mnemonic].func(op1, op2)
        return retval

    def mov(self, x):
        if x >= 0:
            return '>' * x
        else:
            return '<' * abs(x)

    def res(self):
        return '[-]'

    def add(self, x):
        return '+' * x if x >= 0 else self.sub(-x)

    def sub(self, x):
        return '-' * x if x >= 0 else self.add(-x)

    def lin(self, x):
        return ',>' * x

    def out(self, x):
        return '.>' * x

    def jfz(self):
        return '['

    def jbn(self):
        return ']'

    def addi(self, n, x):
        return self.assemble(f"""
            _MOV {n}
            _ADD {x}
            _MOV {-n}
        """)

    def adda(self, n, m):
        """
        ADD address - Adds the value of $m to $n
        :param n: The position of the memory cell corresponding to register n.
        :param m: The position of the memory cell corresponding to register m.
        """
        if n == m:
            return self.assemble(f"MULT {n} 2")

        return self.assemble(f"""
            PUSH {m}          # Push m onto the stack
            _MOV {m}          # Move data pointer to m
            _JFZ            # While m is not 0
              _MOV {n-m}    #   Move data pointer to n
              _ADD 1        #   Add 1 to n
              _MOV {m-n}    #   Move data pointer to m
              _SUB 1        #   Subtract 1 from m
            _JBN            # Repeat until m is 0
            _MOV {-m}
            POPS {m}          # Pop back off the stack into m
        """)

    def aloc(self, varname, n):
        self.data[varname] = self.nextdatacell
        self.nextdatacell += n

    def push(self, n):
        """
        Moves value at memory cell n on to the top of the stack.
        Utilizes the next memory cell on the stack to hold a temporary value.
        :param n: The address of the memory cell to store on the stack. Must not be the stack pointer.
        :return:
        """
        sptr = self.stackpointer
        temp = sptr + 1
        retval = f"""
            _MOV {n}              # Move data pointer to n
            _JFZ                  # Until n is zero
                _MOV {sptr-n}     #   Move data pointer to stack pointer
                _ADD 1            #   Add 1 to stack pointer
                _MOV {temp-sptr}  #   Move data pointer to next cell in stack
                _ADD 1            #   Add 1 to temp
                _MOV {n-temp}     #   Move data pointer back to n
                _SUB 1            #   Subtract 1 from n
            _JBN                  # Repeat until n is zero
            _MOV {temp-n}         # Move data pointer to temp
            _JFZ                  # Until tempn is zero
                _MOV {n-temp}     #   Move data pointer to temp
                _ADD 1            #   Add 1 to n
                _MOV {temp-n}     #   Move data pointer to temp
                _SUB 1            #   Subtract 1 from temp
            _JBN                  # Repeat until temp is 0
            _MOV {-temp}          # Fix data pointer back to 0
        """
        self.stackpointer += 1
        return self.assemble(retval)

    def stor(self, x):
        sptr = self.stackpointer
        self.stackpointer += 1
        return self.assemble(f"""
            _MOV {sptr}         # Move data pointer to the top of the stack
            _ADD {x}            # Add x to the stack
            _MOV {-sptr}        # Fix data pointer back to 0
        """)
    
    def pops(self, n):
        self.stackpointer -= 1
        sptr = self.stackpointer
        return self.assemble(f"""
            _MOV {n}                # Move data pointer to 0
            _RES                    # Set n to 0
            _MOV {sptr-n}           # Move data pointer to top item on stack
            _JFZ                    # Until top stack item is 0
                _MOV {n-sptr}       #   Move data pointer to n
                _ADD 1              #   Add 1 to n
                _MOV {sptr-n}       #   Move data pointer to sptr
                _SUB 1              #   Subtract 1 from sptr
            _JBN                    # Repeat until top of stack is 0
            _MOV {-sptr}            # Fix data pointer back to 0
        """)

    def popn(self):
        self.stackpointer -= 1
        sptr = self.stackpointer
        return self.assemble(f"""
            _MOV {sptr}     # Move data pointer to top of stack
            _RES            # Set the top of the stack to 0
            _MOV {-sptr}    # Fix data pointer back to 0
        """)

    def subi(self, n, x):
        return self.assemble(f"""
            _MOV {n}
            _SUB {x}
            _MOV {-n}
        """)

    def subr(self, n, m):
        # TODO
        pass

    def seti(self, n, x):
        return self.assemble(f"""
            _MOV {n}    # Move data pointer to n
            _RES        # Set n to 0
            _ADD {x}    # Add x to n
            _MOV {-n}   # Fix data pointer back to 0
        """)

    def copy(self, n: int, m: int):
        """
        Copies the value of memory cell m into memory cell n.

        :param n: Destination memory cell
        :param m: Source memory cell
        :return:
        """
        if n == m:
            return ""

        return self.assemble(f"""
            PUSH {m}
            SETI {n} 0
            ADDA {n} {m}
            POPS {m}
        """)

    # I/O INSTRUCTIONS
    def outc(self, n, m):
        """
        Navigates to address n and prints the contents of the next m memory cells.
        :param n: Memory cell address
        :param m: Output length
        """
        return self.assemble(f"""
            _MOV {n}
            _OUT {m}
            _MOV {-(n + m)}
        """)

    def block(self, varname):
        if varname in self.blocks:
            raise f"${varname} is already defined"
        self.currentblock = varname
        self.blocks[varname] = ""

    def endblock(self):
        self.currentblock = None

    def jinz(self, n, v):
        return self.assemble(f"""
            PUSH {n}
            _MOV {n}
            _JFZ
                _MOV {-n}
                {self.assemble(self.blocks[v])}
                _MOV {n}
                _RES
            _JBN
            _MOV {-n}
            POPS {n}
        """)

    def jiez(self, n, v):
        return self.assemble(f"""
            PUSH {n}                                    # Push $n onto the stack
            LNOT {n}                                    # Sets $n to 1 if $n == 0 and 0 otherwise
            _MOV {n}                                    # Move data pointer to n
            _JNZ                                        # If $n is zero
                _MOV {-n}                               #   Fix data pointer back to zero
                POPS {n}                                #   Pop $n off the stack and back into $n
                {self.assemble(self.blocks[v])}         #   Inline the linked block
                PUSH {n}                                #   Push $n back onto the stack
                _MOV {n}                                #   Move data pointer back to $n
                _RES                                    #   Set $n to zero
            _JBN                                        # End if
            _MOV {-n}                                   # Fix data pointer back to zero
            POPS {n}                                    # Pop $n off the stack and back into $n
        """)

    def lnot(self, n):
        temp0 = self.data['temp0']
        return self.assemble(f"""
            _MOV {temp0}                    # Move data pointer to temp0
            _RES                            # Set temp0 to 0
            _MOV {n - temp0}                # Move data pointer to n
            _JFZ                            # If $n is not zero
                _MOV {temp0 - n}            #   Move data pointer to temp0
                _ADD 1                      #   Set temp0 to 1
                _MOV {n - temp0}            #   Move data pointer to n
                _RES                        #   Set n to 0
            _JBN                            # End if
            _ADD 1                          
            _MOV {temp0 - n}
            _JFZ
                _MOV {n - temp0}
                _SUB 1
                _MOV {temp0 - n}
                _SUB 1
            _JBN
            _MOV {-temp0}
        """)

    def mult(self, n, x):
        sptr = self.stackpointer
        return self.assemble(f"""
            PUSH {n}            # Push n onto the stack
            _MOV {sptr}         # Move data pointer to top of stack
            _JFZ                # While top of stack is not 0
                _MOV {n-sptr}   #   Move data pointer to n
                _ADD {x-1}      #   Add x-1 to n
                _MOV {sptr-n}   #   Move data pointer to top of stack
                _SUB 1          #   Subtract 1 from top of stack
            _JBN                # Repeat until top of stack is equal to 0
            _MOV {-sptr}        # Fix data pointer back to 0
            POPN                # Fix stack pointer back down
        """)