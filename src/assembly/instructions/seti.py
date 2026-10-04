from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Seti(AssemblerMixin):

    def seti_definitions(self):
        return {
            ("SETI", ("$sp", "$sp")): self.seti_sp_sp,
            ("SETI", ("register", "register")): self.seti_rt_rs
        }

    def seti_rt_rs(self, rt, rs):
        return self.assemble(f"""
            PUSH {rs.mnemonic()}
            PUSH {rt.mnemonic()}
            SETI $sp $sp
        """)

    def seti_sp_sp(self, sp1, sp2):
        """
        SETI (SET INDIRECT 8-BIT)

        Pops an address off the stack. Pops a value off the stack.
        Sets the cell at that address to the provided value.

        1. Set up initial state [... v a|0 0] > [... v a a 0]
        """
        source = self.assemble(f"""
            _CPY:16 2 4
            _MDP 2
            _ADD:16 2
            PUSH 6
            SUBT $sp $sp $sp
            SWAP $sp $sp
            SUBT $sp $sp $sp
            PUSH $sp
            _MOV:16 2
            _MDP -2
            _JFZ
                _MDP -6
                _MOV:16 8
                _MDP 2
                _MOV:16 -2
                _MDP 2
                _MOV:16 -2
                _MDP 2
                _MOV:16 -2
                _MDP -2
                _SUB:16 2 2 3
            _JBN
            _MDP 1
            _JFZ
                _MDP -7
                _MOV:16 8
                _MDP 2
                _MOV:16 -2
                _MDP 2
                _MOV:16 -2
                _MDP 2
                _MOV:16 -2
                _MDP -2
                _SUB:16 2 2 3
                _JFZ
                    _MDP -6
                    _MOV:16 8
                    _MDP 2
                    _MOV:16 -2
                    _MDP 2
                    _MOV:16 -2
                    _MDP 2
                    _MOV:16 -2
                    _MDP -2
                    _SUB:16 2 2 3
                _JBN
                _MDP 1
            _JBN
            _MDP -7
            _SET:16 0
            _MDP 2
            _MOV:16 -2
            _MDP 2
            _JFZ
                _MOV:16 2
                _MDP 6
                _MOV:16 -8
                _MDP -4
                _SUB:16 2 2 3
            _JBN
            _MDP 1
            _JFZ
                _MDP -1
                _MOV:16 2
                _MDP 6
                _MOV:16 -8
                _MDP -4
                _SUB:16 2 2 3
                _JFZ
                    _MOV:16 2
                    _MDP 6
                    _MOV:16 -8
                    _MDP -4
                    _SUB:16 2 2 3
                _JBN
                _MDP 1
            _JBN
            _MDP 5
            _MOV:16 -8
            _MDP -8
            _SUB:16 6 2 3
            """)
        return source


