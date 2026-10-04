from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Swap(AssemblerMixin):

    def swap_definitions(self):
        return {
            ("SWAP", ("$sp", "$sp")): self.swap_sp_sp,
        }

    def swap_sp_sp(self, sp1, sp2):
        """
        SWAP $sp $sp

        BEHAVIOR:
            1. Swaps the top value on the stack with the 2nd top value.
            2. Stack pointer remains unchanged.

        EXAMPLE:
            [0 0 4 0 3 0 6 0] > [0 0 3 0 4 0 6 0]
        """
        return self.assemble(f"""
            _MDP -2
            _MOV:16 4
            _MDP -2
            _MOV:16 2
            _MDP 6
            _MOV:16 -6
            _MDP -2
        """)