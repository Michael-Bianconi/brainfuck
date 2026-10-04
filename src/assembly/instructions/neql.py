from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Neql(AssemblerMixin):

    def neql_definitions(self):
        return {
            ("NEQL", ("$sp", "immediate")): self.neql_sp_imm,
            ("NEQL", ("register", "immediate")): self.neql_rt_imm
        }

    def neql_sp_imm(self, sp, imm):
        """
        NEQL $sp imm (NOT EQUALS)

        Pops the top value off the stack. If it equals the provided
        immediate, push 0 onto the stack. If it does not equal the
        immediate, push 1 onto the stack.
        """
        return self.assemble(f"""
            _MDP -2
            _NEQ:16 {imm} 4
            _MDP 2
        """)

    def neql_rt_imm(self, rt, imm):
        """
        NEQL $rt imm (NOT EQUALS)

        Fetches value of register. If it equals the provided
        immediate, set register to 0. If it does not equal the
        immediate, set register to 1.
        """
        return self.assemble(f"""
            PUSH {rt.mnemonic()}
            NEQL $sp {imm}
            POPS {rt.mnemonic()}
        """)



