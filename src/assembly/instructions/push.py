from src.assembly.instructions.assembler_mixin import AssemblerMixin


class Push(AssemblerMixin):

    def push_definitions(self):
        return {
            ("PUSH", ("immediate",)): self.push_immediate,
            ("PUSH", ("register",)): self.push_register,
            ("PUSH", ("$sp",)): self.push_sp,
            ("PUSH", ("label",)): self.push_label,
        }

    def push_immediate(self, immediate):
        """
        PUSH imm

        BEHAVIOR:
            1. Pushes the provided 16-bit immediate value onto the stack.
            2. Increments the stack pointer by 2.

        EXAMPLE:
            PUSH 5
            [0 0 2 0] > [0 0 5 0 4 0]
        """
        return self.assemble(f"""
            _MOV:16 4    
            _ADD:16 {immediate}
            _MDR:8 4
            _ADD:16 2
            _MOV:16 -2
            _MDL:8 2
        """)

    def push_register(self, register):
        """
        PUSH $rt

        Push the register's value onto the stack.
        """
        return self.assemble(f"""
            PUSH {register.address()}
            GETI $sp $sp
        """)

    def push_sp(self, sp):
        """
        PUSH $sp

        BEHAVIOR:
            1. Pushes the top value on the stack to the top of the stack (copying it).
            2. Increments stack pointer by 2.

        EXAMPLE:
            [0 0 2 0 4 0] > [0 0 2 0 2 0 6 0]
        """
        return self.assemble(f"""
            _CPY:16 2 4
            _SET:16 0
            _MDL 2
            _CPY:16 2 8
            _MDR 4
            _ADD:16 2
        """)

    def push_label(self, label):
        raise NotImplementedError("PUSH label")