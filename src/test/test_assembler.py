from unittest import TestCase

from src.assembly.assembler import Assembler
from src.interpreter.interpreter import Interpreter
from src.interpreter.optimizedinterpreter import OptimizedInterpreter


class TestAssembler(TestCase):

    def setUp(self) -> None:
        self.assembler = Assembler()
        self.interpreter = OptimizedInterpreter()

    def assertStackContents(self, expected_content, expected_pointer):
        """

        :param expected_content: The top n values on the stack.
        :param expected_pointer: The position of the stack pointer.
        :return:
        """
        start = self.assembler.stack_pointer - len(expected_content)
        actual_content = self.interpreter.memory[start:self.assembler.stack_pointer]
        self.assertListEqual(actual_content, expected_content, msg=f"Expected {expected_content} got {actual_content}")
        self.assertEqual(self.assembler.stack_pointer, expected_pointer, msg=self.dump_interpreter())
        self.assertListEqual(self.interpreter.memory[expected_pointer:expected_pointer+10], [0] * 10,
                             msg='Expected cells past stack pointer to be empty' + self.dump_interpreter())
        self.assertEqual(self.assembler.stack_pointer, self.interpreter.dptr)

    def to16bit(self, i):
        lo = (i % 65536) & 0b0000000011111111
        hi = ((i % 65536) & 0b1111111100000000) >> 8
        return [lo, hi]

    def dump_interpreter(self):
        memory = ''
        pointers = ''
        for i in range(self.assembler.stack_pointer + 10):
            cell = str(self.interpreter.memory[i])
            memory += cell + ' '
            pointers += 's' if i == self.assembler.stack_pointer else 'd' if i == self.interpreter.dptr else ' '
            pointers += ' ' * len(cell)

        return '\n' + memory + '\n' + pointers

    def cases_immediate8(self):
        return [0, 1, 5, 10, 25, 255]

    def cases_immediate8_immediate8(self):
        return [
            [0, 0], [0, 1], [1, 0], [1, 1], [5, 10], [255, 0], [0, 255], [255, 255]
        ]

    def run_and_check(self, cases, source, check):
        for case in cases:
            with self.subTest(values=case):
                self.setUp()
                exe = self.assembler.assemble(source(case))
                self.interpreter.run(exe)
                check(case)

    def tearDown(self):
        print(f"Instructions: {len(self.interpreter.source)}")
        print(f"Cycles: {self.interpreter.cycles}")
