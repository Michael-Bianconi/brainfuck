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
            [0 0 5 0 3 0 6 0] > [0 0 2 0 4 0]
        """
        return self.assemble(f"""
            _MOV:16 4
            _MDL 2
            _MOV:16 2
            _MDR 3
            _JFZ
                _MDL 5
                _SUB:16 256
                _MDR 4
                _SUB:16 256
                _MDR 1
            _JBN
            _MDL 1
            _JFZ      
                _MDL:8 4
                _SUB:16 1
                _MDR:8 4
                _SUB:16 1
            _JBN
            _MDR 4
            _SUB:16 2
            _MOV:16 -6
            _MDL 6    
        """)