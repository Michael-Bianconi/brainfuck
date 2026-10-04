from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Plus(AssemblerMixin):

    def plus_definitions(self):
        return {
            ("PLUS", ("$sp", "$sp")): self.plus_sp_sp,
            ("PLUS", ("$sp", "immediate")): self.plus_sp_immediate,
            ("PLUS", ("register", "register")): self.plus_rt_rs,
            ("PLUS", ("register", "immediate")): self.plus_rt_imm,
        }

    def plus_sp_sp(self, sp1, sp2):
        """
        PLUS $sp $sp

        BEHAVIOR:
            1. Pops the top two 16-bit values off the stack, adds them together,
               and places the sum back on the stack.
            2. Decrements stack pointer by 2.

        EXAMPLE:
            PLUS @top @top @top
            [0 0 5 0 3 0 6 0] > [0 0 8 0 4 0]
        """
        return self.assemble(f"""
            _MOV:16 4
            _MDP -2
            _MOV:16 2
            _MDP 3
            _JFZ
                _MDP -5
                _ADD:16 256
                _MDP 4
                _SUB:16 256
                _MDP 1
            _JBN
            _MDP -1
            _JFZ      
                _MDP -4
                _ADD:16 1
                _MDP:8 4
                _SUB:16 1
            _JBN
            _MDP 4
            _SUB:16 2
            _MOV:16 -6
            _MDP -6
        """)

    def plus_sp_immediate(self, sp, immediate):
        """
        PLUS:16 @TOP @TOP IMM

        BEHAVIOR:
            1. Adds an immediate value to the value at the top of the stack.
            2. Stack pointer remains unchanged.

        EXAMPLE:
            PLUS @top @top 3
            [0 0 5 0 4 0] > [0 0 8 0 4 0]
        """
        return self.assemble(f"""
            PUSH {immediate}
            PLUS $sp $sp
        """)

    def plus_rt_rs(self, rt, rs):
        """
        PLUS $rt $rs

        Adds the value in $rs to the value in $rt.
        """
        return self.assemble(f"""
            PUSH {rt.mnemonic()}
            PUSH {rs.mnemonic()}
            PLUS $sp $sp
            POPV {rt.mnemonic()}
        """)

    def plus_rt_imm(self, rt, imm):
        return self.assemble(f"""
            PUSH {rt.mnemonic()}
            PUSH {imm}
            PLUS $sp $sp
            POPV {rt.mnemonic()}
        """)