from src.assembly.instruction import Instruction
from src.assembly.parser import Symbol, Immediate, Top, Address


class MemoryMixin:

    def memory_definitions(self):
        return {
            "ALOC": Instruction(self.aloc, [
                [Symbol, Immediate]]),
            "PUSH": Instruction(self.push, [
                [Top, Immediate],
                [Top, Address],
                [Top, Top],
                [Address, Top],
                [Address, Immediate]]),
            "POPV": Instruction(self.popv, [
                [Top],
                [Address, Top]]),
            "SWAP": Instruction(self.swap, [
                [Top, Top]
            ])
        }

    def aloc(self, operands, operand_types):
        """
        Allocates space for a variable on the stack. Stores variable name in vtable.
        Moves stack pointer to next position.
        :param v: Address lael
        :param x: Value to store in the allocated memory
        :return:
        """
        symbol, immediate = operands
        num_values, bitwidth = immediate.value, immediate.bitwidth

        self.vtable[symbol.value] = self.stack_pointer

        if bitwidth == 8:
            self.stack_pointer += num_values
            return ">"

        elif bitwidth == 16:
            self.stack_pointer += num_values * 4
            return ">>>>"

    def push(self, operands, operand_types):
        """
        Copies the value at address a to the top of the stack.
        :param a:
        :return:
        """
        dest, source = operands

        # Push immediate value onto the stack
        if operand_types == [Top, Immediate]:
            return self._push_top_immediate(dest, source)

        # Push value at known address onto the stack
        elif operand_types == [Top, Address] and not source.indirect:
            return self._push_top_direct(dest, source)

        elif operand_types == [Top, Address] and source.indirect:
            return NotImplementedError()

        elif operand_types == [Top, Top]:
            return self._push_top_top(dest, source)

        elif operand_types == [Address, Immediate] and not dest.indirect:
            return self._push_direct_immediate(dest, source)

        elif operand_types == [Address, Immediate] and dest.indirect:
            raise NotImplementedError()

        elif operand_types == [Address, Address]:
            raise NotImplementedError()

        else:
            raise NotImplementedError()

    def _push_top_immediate(self, dest, source):
        self.stack_pointer += 1 if dest.bitwidth == 8 else 4
        return self.assemble(f"""
                         _ADD {source.value}:{dest.bitwidth}
                         _RIT 1:{dest.bitwidth}
                     """)

    def _push_top_direct(self, dest, source):
        address = source.resolve_direct(self.vtable)
        offset = self.stack_pointer - address
        if dest.bitwidth == 8 and source.base.bitwidth == 8:
            self.stack_pointer += 1
            return self.assemble(f"""
                 _LFT {offset}
                 _JFZ
                     _SUB 1
                     _RIT {offset}
                     _ADD 1
                     _RIT 1
                     _ADD 1
                     _LFT {offset + 1}
                 _JBN
                 _RIT {offset + 1}
                 _JFZ
                     _SUB 1
                     _LFT {offset + 1}
                     _ADD 1
                     _RIT {offset + 1}
                 _JBN
             """)
        elif dest.bitwidth == 16 and source.base.bitwidth == 16:
            return self.assemble(f"""
                 PUSH @top @{address}:8
                 PUSH @top @{address + 1}:8
                 PUSH @top 0
                 PUSH @top 0
             """)
        else:
            raise NotImplementedError()

    def _push_direct_immediate(self, dest, source):
        offset = self.stack_pointer - dest.resolve_direct(self.vtable)
        return self.assemble(f"""
             _LFT {offset}
             _SET 0
             _ADD {source.value}:{dest.base.bitwidth}
             _RIT {offset}
         """)

    def _push_top_top(self, dest, source):
        if dest.bitwidth == 8 and source.bitwidth == 8:
            return self.assemble(f"PUSH @top @{self.stack_pointer - 1}")
        elif dest.bitwidth == 16 and source.bitwidth == 16:
            return self.assemble(f"PUSH @top:16 @{self.stack_pointer - 4}:16")
        else:
            raise NotImplementedError()

    def swap(self, operands, operand_types):
        """
        Pops b off the stack. Pops a off the stack. Pushes b onto the stack. Pushes a onto the stack.
        :param bitwidth:
        :return:
        """
        dest, source = operands
        if operand_types == [Top, Top] and dest.bitwidth == 8 and source.bitwidth == 8:
            return ''.join([                    # [a, b | 0]
                '<[>+<-]',                      # [a | 0, b]
                '<[>+<-]>>',                    # [0, a | b]
                '[<<+>>-]'                      # [b, a | 0]
            ])
        else:
            raise NotImplementedError()

    def popv(self, operands, operand_types):
        if operand_types == [Top]:
            bitwidth = operands[0].bitwidth
            if bitwidth == 8:
                self.stack_pointer -= 1
                return '<[-]'
            elif bitwidth == 16:
                self.stack_pointer -= 4
                return '<<<[-]<[-]'
        elif operand_types == [Address, Top] and operands[0].base.bitwidth == 8:
            dest = operands[0].resolve_direct(self.vtable)
            offset = (self.stack_pointer - dest) - 1
            source = self.assemble(f"""
                PUSH @{dest} 0      # Set dest to 0
                _LFT 1              # Move data pointer to top value on the stack
                _JFZ                # While top value is nonzero
                    _LFT {offset}   #   Move to dest
                    _ADD 1          #   Add 1
                    _RIT {offset}   #   Move to top
                    _SUB 1          #   Sub 1
                _JBN                # Repeat until top is zero
            """)
            self.stack_pointer -= 1
            return source
        else:
            raise NotImplementedError()
