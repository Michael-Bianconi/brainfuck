from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Subt(AssemblerMixin):

    def subt_definitions(self):
        return {
            ("SUBT", ("$sp", "$sp", "$sp")): self.subt_sp_sp_sp,
        }

    def subt_sp_sp_sp(self, sp1, sp2, sp3):
        """
        SUBT $sp $sp $sp (SUBTRACT)

        BEHAVIOR:
            1. Pops the top two values off the stack. Subtracts the top value from
               the 2nd value on the stack. Pushes the result onto the stack.
            2. Decrements the stack pointer by 2.

        EXAMPLE:
            [0 0 5 0 0 0 3 0 0 0 6 0] > [0 0 2 0 4 0]
            [0 0 5 0 3 0 6 0] > [0 0 2 0 4 0]
        """
        return self.assemble(f"""
            _MDP -1                 # Move to high bits of y
            _JFZ
                _MDP -3             # Move to low bits of x
                _SUB:16 256 6 7
                _MDP 2              # Move to low bits of y
                _SUB:16 256 4 5
                _MDP 1              # Move to high bits of y
            _JBN
            _MDP -1                 # Move to low bits of y
            _JFZ      
                _MDP -2             # Move to low bits of x
                _SUB:16 1 6 7
                _MDP 2              # Move to low bits of y
                _SUB:16 1 4 5
            _JBN
            _MDP 2                  # Move to stack pointer
            _SUB:16 2 2 3
            _MOV:16 -2
            _MDP -2
        """)