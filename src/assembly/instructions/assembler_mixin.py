from typing import Protocol


class AssemblerMixin(Protocol):
    defining_func: str or None
    assemble: callable
    vtable: dict
    stack_pointer: int