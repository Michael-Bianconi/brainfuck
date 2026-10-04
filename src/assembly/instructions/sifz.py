from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Sifz(AssemblerMixin):

    def sifz_definitions(self):
        return {
            ("SIFZ", ("register",)): self.sifz_rt,
            ("ZFIS", ("register",)): self.zfis_rt,
        }

    def sifz_rt(self, rt):
        """
        SIFZ $rt (SKIP IF ZERO)

        Pushes $rt onto the stack. If $rt is non-zero, execute all instructions
        until closing ZFIS instruction. If $rt is zero, skip to enclosing ZFIS
        instruction.

        BF ASSEMBLY ONLY. DOES NOT ASSEMBLE TO BFM.
        Since this instruction relies on an enclosing instruction, assembly
        to .bfm is not possible. See JUMP instead.
        """

        return self.assemble(f"""
            PUSH {rt.mnemonic()}
            NEQL $sp 0
            _RAW <<[>>
            POPS
        """)

    def zfis_rt(self, rt):
        return self.assemble(f"""
            PUSH {rt.mnemonic()}
            NEQL $sp 0
            _RAW <<]>>
            POPS
        """)



