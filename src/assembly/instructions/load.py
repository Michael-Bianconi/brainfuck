from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Load(AssemblerMixin):

    def load_definitions(self):
        return {
            ("LOAD", ("register", "immediate",)): self.load_rt_imm,
            ("LOAD", ("register", "register",)): self.load_rt_rs,
        }

    def load_rt_imm(self, rt, imm):
        """
        LOAD $rt imm

        BEHAVIOR:
            1. Sets register to immediate value
        """
        return self.assemble(f"""
            PUSH {imm}
            PUSH {rt.address()}
            SETI $sp $sp
        """)

    def load_rt_rs(self, rt, rs):
        """
        LOAD $rt $rs

        BEHAVIOR:
            1. Sets $rt to $rs
        """
        return self.assemble(f"""
            GETI $sp {rs.mnemonic()}
            PUSH {rt.address()}
            SETI $sp $sp
        """)