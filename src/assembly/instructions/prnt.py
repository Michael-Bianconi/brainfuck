from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Prnt(AssemblerMixin):

    def prnt_definitions(self):
        return {
            ("PRNT", ("$sp", "immediate")): self.prnt_sp_imm,
            ("PRNT", ("register",)): self.prnt_reg,
        }

    def prnt_sp_imm(self, sp, imm):
        """
        PRNT $sp imm (PRINT)

        Pops the top N values off the stack. Prints them in the order
        they are popped.

        Note: Only the lower 8 bits of each 16-bit stack value are considered.
        Example: 0xFFAD is behaviorally equivalent to 0x00AD
        """
        if imm == 0:
            return ""
        return self.assemble(f"""
            _MDP -2
            _SOA 1
            _MDP 2
            POPS
        """ * imm)

    def prnt_reg(self, rt):
        """
        PRNT $rt imm

        Prints all cells, starting at the address held in $rt and continuing until a cell
        with 0 is reached.

        0 1 2 3 4 5 6 7 8 9 A B
        H E L L O   W O R L D \0
        """
        return self.assemble(f"""
            GETI $sp {rt.mnemonic()}
            _MDP -2
            _JFZ
                _SOA 2
                _MDP 2
                POPS
                PLUS {rt.mnemonic()} 1
                GETI $sp {rt.mnemonic()}
                _MDP -2
            _JBN
            _MDP 2 
        """)