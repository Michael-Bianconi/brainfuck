from src.assembly.instructions.assembler_mixin import AssemblerMixin


class MemoryMixin(AssemblerMixin):

    def memory_definitions(self):
        return {
            ("ALOC", ("Symbol", "Immediate")): self.aloc_8,
            ("ALOC:16", ("Symbol", "Immediate")): self.aloc_16,

            ("GIBW", ("Immediate",)): self.gibw,

            ("GETI", ("Top", "Top")): self.geti_8_8_top_top,

            ("PUSH", ("Top", "Top")): self.push_8_8_top_top,
            ("PUSH", ("Top", "Immediate")): self.push_8_top_immediate,
            ("PUSH", ("Top", "Address")): self.push_8_8_top_address,
            ("PUSH", ("Address", "Immediate")): self.push_8_address_immediate,

            ("PUSH:16", ("Top", "Top")): self.push_16_16_top_top,
            ("PUSH:16", ("Top", "Immediate")): self.push_16_top_immediate,
            ("PUSH:16", ("Top", "Address")): self.push_16_16_top_address,
            ("PUSH:16", ("Address", "Immediate")): self.push_16_address_immediate,

            ("POPV", ("Top",)): self.popv_8_top,
            ("POPV", ("Address", "Top")): self.popv_8_8_address_top,

            ("POPV:16", ("Top",)): self.popv_16_top,
            ("POPV:16", ("Address", "Top")): self.popv_8_8_address_top,

            ("SETI", ("Top", "Top")): self.seti_8_8_top_top,

            ("SWAP", ("Top", "Top")): self.swap_8_8_top_top,
        }

    def aloc_8(self, symbol, immediate):
        """
        Allocates space for a variable on the stack. Stores variable name in vtable.
        Moves stack pointer to next position.
        :param v: Address lael
        :param x: Value to store in the allocated memory
        :return:
        """
        self.vtable[symbol] = self.stack_pointer
        self.stack_pointer += immediate
        return ">"

    def aloc_16(self, symbol, immediate):
        self.vtable[symbol] = self.stack_pointer
        self.stack_pointer += immediate * 4
        return ">>>>"

    def push_8_8_top_top(self, top1, top2):
        return self.assemble(f"PUSH @top @{self.stack_pointer - 1}")

    def push_16_16_top_top(self, top1, top2):
        return self.assemble(f"PUSH:16:16 @top @{self.stack_pointer - 4}")

    def push_8_top_immediate(self, top, immediate):
        self.stack_pointer += 1
        return self.assemble(f"""
             _ADD {immediate}
             _RIT 1
         """)

    def push_16_top_immediate(self, top, immediate):
        self.stack_pointer += 4
        return self.assemble(f"""
             _ADD:16 {immediate}
             _RIT:16 1
         """)

    def push_8_8_top_address(self, top, address):
        offset = self.stack_pointer - address
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

    def push_16_16_top_address(self, top, address):
        return self.assemble(f"""
             PUSH @top @{address}
             PUSH @top @{address + 1}
             PUSH @top 0
             PUSH @top 0
         """)

    def push_8_address_immediate(self, address, immediate):
        offset = self.stack_pointer - address
        self.stack_pointer += 1
        return self.assemble(f"""
             _LFT {offset}
             _SET 0
             _ADD {immediate}
             _RIT {offset}
         """)

    def push_16_address_immediate(self, address, immediate):
        offset = self.stack_pointer - address
        self.stack_pointer += 4
        return self.assemble(f"""
             _LFT {offset}
             _SET:16 0
             _ADD:16 {immediate}
             _RIT {offset}
         """)

    def geti_8_8_top_top(self, top1, top2):
        """
        Pops an address off the stack. Pushes the value at that address onto the stack.

        :param a: The address of the first cell in the array of cells. Set to 0 for absolute address.
        :param bitwidth:
        :return: Pushes a[i] onto the stack.
        """
        return self.assemble(f"""
            PUSH @top 0                 # [a ... x ... i 0 | 0]
            SWAP @top @top              # [a ... x ... 0 i | 0]
            _RAW <[[>]+[<]>-]>[>]       # [a ... x ... 0 0 1 ... 1 1 | 0]
            PUSH @top @0                # [a ... x ... 0 0 1 ... 1 1 | x]
            _RAW <<[->[<+>-]<<]>>       # [a ... x ... 0 0 x | 0]
            SWAP @top @top
            POPV @top
            SWAP @top @top
            POPV @top                   # [a ... x ... x | 0]
        """)

    def seti_8_8_top_top(self, top1, top2):
        source = self.assemble(f"""
                PUSH @top 0                             # [... x ... v i 0 | 0]
                SWAP @top @top                          # [... x ... v 0 i | 0]
                _RAW <[[>]+[<]>-]>[>]+                  # [... x ... v 0 0 S 1 ... 1 | 0]
                _RAW <[<]<<[>>>[>]<+[<]<<-]>>>[>]<->    # [... x ... 0 0 0 S 1 ... 1 v | 0
                POPV @-1 @top                           # [... v ... 0 0 S 0 1 ... 1 | 0 0]
                _RAW <[-<]<<                            # [... x ... | 0]
            """)
        self.stack_pointer -= 2
        return source

    def swap_8_8_top_top(self,  top1, top2):
        """
        Pops b off the stack. Pops a off the stack. Pushes b onto the stack. Pushes a onto the stack.
        :param bitwidth:
        :return:
        """
        return ''.join([                    # [a, b | 0]
            '<[>+<-]',                      # [a | 0, b]
            '<[>+<-]>>',                    # [0, a | b]
            '[<<+>>-]'                      # [b, a | 0]
        ])

    def popv_8_top(self, top):
        self.stack_pointer -= 1
        return '<[-]'

    def popv_16_top(self, top):
        self.stack_pointer -= 4
        return '<<<[-]<[-]'

    def popv_8_8_address_top(self, address, top):
        offset = (self.stack_pointer - address) - 1
        source = self.assemble(f"""
            PUSH @{address} 0      # Set dest to 0
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

    def gibw(self, immediate):
        return "PUSH @top 8" if immediate < 256 else "PUSH @top 16"
