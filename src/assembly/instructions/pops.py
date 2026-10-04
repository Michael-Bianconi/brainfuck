from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Pops(AssemblerMixin):

    def pops_definitions(self):
        return {
            ("POPS", ()): self.pops,
            ("POPS", ("register",)): self.pops_rt,
        }

    def pops(self):
        """
        POPS (POP STACK)

        Pops top value from stack. Reduces stack pointer by 2.
        :return:
        """
        return self.assemble(f"""
            _MDP -2
            _SET:16 0
            _MDP 2
            _MOV:16 -2
            _MDP -2
            _SUB:16 2
        """)

    def pops_rt(self, rt):
        return self.assemble(f"""
            PUSH {rt.address()}
            SETI $sp $sp
        """)



