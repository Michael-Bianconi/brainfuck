from typing import Protocol


class AssemblerMixin(Protocol):
    assemble: callable
    vtable: dict
    stack_pointer: int