from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Popv(AssemblerMixin):

    def popv_definitions(self):
        return {
            ("POPV", ("register",)): self.popv_rt
        }

    def popv_rt(self, rt):
        return self.assemble(f"""
            PUSH {rt.address()}
            SETI $sp $sp
        """)



