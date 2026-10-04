from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Band(AssemblerMixin):

    def band_definitions(self):
        return {
            ("BAND", ("$sp", "immediate")): self.band_sp_imm,
            ("BAND", ("register", "immediate")): self.band_rt_imm,
        }

    def band_sp_imm(self, sp, imm):
        """
        BAND $sp imm (BITWISE AND)
        """
        if imm == 0x0000:
            return self.assemble(f"""
                _RAW <[-]<[-]>>
            """)
        elif imm == 0x00FF:
            return self.assemble(f"""
                _RAW <[-]>
            """)
        elif imm == 0xFF00:
            return self.assemble(f"""
                _RAW <<[-]>>
            """)
        elif imm == 0xFFFF:
            return ""
        else:
            raise NotImplementedError(f"BAND $sp {imm}")

    def band_rt_imm(self, rt, imm):
        return self.assemble(f"""
            PUSH {rt.mnemonic()}
            BAND $sp {imm}
            POPS {rt.mnemonic()}
        """)


