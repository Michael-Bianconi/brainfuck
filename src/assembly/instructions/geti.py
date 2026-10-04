from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Geti(AssemblerMixin):

    def geti_definitions(self):

        return {
            ("GETI", ("register", "register")): self.geti_rt_rs,
            ("GETI", ("$sp", "register")): self.geti_sp_rs,
            ("GETI", ("$sp", "$sp")): self.geti_sp_sp,
        }

    def geti_rt_rs(self, rt, rs):
        return self.assemble(f"""
            GETI $sp {rs.mnemonic()}
            POPV {rt.mnemonic()}
        """)

    def geti_sp_rs(self, sp, rs):
        return self.assemble(f"""
            PUSH {rs.address()}
            GETI $sp $sp
        """)

    def geti_sp_sp(self, sp1, sp2):
        """
        GETI $sp $sp

        BEHAVIOR:
            1. Pops an absolute address off the stack. Pushes the 16-bit value at that
               location in memory onto the stack.
            2. Stack pointer remains unchanged.

        EXAMPLE:
            GETI @top @top
            [5 0 6 0 7 0 2 0 8 0] > [5 0 6 0 7 0 7 0 8 0]
            [5 0 6 0 7 0 2 0 8 0] > [5 0 6 0 7 0 7 0 8 0]

        NOTES:
            1. The address MUST be a multiple of 2, and be at least 4 less than the stack pointer
               (it cannot point to the address being used for this instruction).
        """
        return self.assemble(f"""
                    _CPY:16 2 4
                    _MDP 2
                    _ADD:16 2
                    PUSH 4
                    SUBT $sp $sp $sp
                    SWAP $sp $sp
                    SUBT $sp $sp $sp
                    PUSH 0
                    SWAP $sp $sp
                    PUSH $sp
                    _MOV:16 4
                    _MDP -2
                    _JFZ
                        _MDP -6
                        _MOV:16 8
                        _MDP 4
                        _MOV:16 -2
                        _MDP 2
                        _MOV:16 -2
                        _MDP -2
                        _SUB:16 2 2 3
                    _JBN
                    _MDP 1
                    _JFZ
                        _MDP -1
                        _MDP -6
                        _MOV:16 8
                        _MDP 4
                        _MOV:16 -2
                        _MDP 2
                        _MOV:16 -2
                        _MDP -2
                        _SUB:16 2 2 3
                        _JFZ
                            _MDP -6
                            _MOV:16 8
                            _MDP 4
                            _MOV:16 -2
                            _MDP 2
                            _MOV:16 -2
                            _MDP -2
                            _SUB:16 2 2 3
                        _JBN
                        _MDP 1
                    _JBN
                    _MDP -1
                    _MDP -6
                    _CPY:16 2 6
                    _MDP 4
                    _JFZ
                        _MOV:16 2
                        _MDP -2
                        _MOV:16 2
                        _MDP 8
                        _MOV:16 -8
                        _MDP -4
                        _SUB:16 2 2 3
                    _JBN

                    _MDP 1
                    _JFZ
                        _MDP -1
                        _MOV:16 2
                        _MDP -2
                        _MOV:16 2
                        _MDP 8
                        _MOV:16 -8
                        _MDP -4
                        _SUB:16 2 2 3
                        _JFZ
                            _MOV:16 2
                            _MDP -2
                            _MOV:16 2
                            _MDP 8
                            _MOV:16 -8
                            _MDP -4
                            _SUB:16 2 2 3
                        _JBN
                        _MDP 1
                    _JBN
                    _MDP -1
                    _MDP 8
                    _MOV:16 -8
                    _MDP -8
                    _SUB:16 4 2 3
                """)