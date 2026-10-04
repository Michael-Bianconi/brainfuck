from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Bshr(AssemblerMixin):
    """
    BITWISE SHIFT RIGHT
    """

    def bshr_definitions(self):
        return {
            ("BSHR", ("$sp", "immediate")): self.bshr_sp_imm,
            ("BSHR", ("register", "immediate")): self.bshr_rt_imm,
        }

    def bshr_sp_imm(self, sp, imm):
        if imm == 16:
            return self.assemble(f"""
                _RAW <[-]<[-]>>
            """)
        elif imm == 8:
            return self.assemble(f"""
                _MDP -1
                _SET 0
                _MDP -1
                _MOV 1
                _MDP 2
            """)
        elif imm == 0:
            return ""
        else:
            raise NotImplementedError(f"BSHR $sp {imm}")

    def bshr_rt_imm(self, rt, imm):
        return self.assemble(f"""
            PUSH {rt.mnemonic()}
            BSHR $sp {imm}
            POPS {rt.mnemonic()}
        """)


