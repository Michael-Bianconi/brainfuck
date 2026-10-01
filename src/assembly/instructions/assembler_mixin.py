from typing import Protocol


class AssemblerMixin(Protocol):
    defining_func: str or None
    assemble: callable
    vtable: dict
    stack_pointer: int

    def i_inst(self, opcode, register, immediate):
        """
        oooooooo rrrrrrrr iiiiiiii iiiiiiii
        """
        immediate = immediate % 65536
        register = (register % 256) << 16
        opcode = (opcode % 256) << 24
        return opcode | register | immediate
