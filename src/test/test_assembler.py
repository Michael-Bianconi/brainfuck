from io import StringIO
from unittest import TestCase

from src.assembly.assembler import Assembler
from src.interpreter.interpreter import Interpreter
from src.interpreter.optimizedinterpreter import OptimizedInterpreter


class TestAssembler(TestCase):

    def setUp(self) -> None:
        register_count = 32
        text_size = 256
        self.assembler = Assembler()
        self.interpreter = OptimizedInterpreter(stdout=StringIO())
        self.vm_source = self.assembler.init_vm(register_count, text_size)
        self.prog_start = (register_count * 2) + text_size + 2

    def assertStdout(self, expected):
        self.interpreter.stdout.seek(0)
        actual = self.interpreter.stdout.read()
        self.assertEqual(actual, expected, msg="Standard output mismatch")

    def assertRegisters(self, values):
        register_ordinals = ["$c0", "$c1", "$v0", "$v1"]
        actual = self.interpreter.memory[0: len(register_ordinals) * 2]
        expected = []
        for i in register_ordinals:
            if i in values:
                expected.extend(self.to16bit(values[i]))
            else:
                expected.extend([0, 0])
        self.assertEqual(actual, expected, msg="Register mismatch")

    def assertDataPointerAlignsWithStackPointer(self, num_bytes_pushed):
        self.assertEqual(self.sp, self.prog_start + num_bytes_pushed, msg="Stack pointer mismatch")
        self.assertEqual(self.dptr, self.sp, msg=f"Data pointer mismatch")

    def assertStackContents(self, expected_content):
        """
        :param expected_content: The top n values on the stack.
        :return:
        """
        actual_content = self.get_stack_contents(len(expected_content))
        self.assertListEqual(actual_content, expected_content, msg=f"Expected stack {expected_content} got {actual_content}")

    def to16bit(self, i):
        lo = (i % 65536) & 0b0000000011111111
        hi = ((i % 65536) & 0b1111111100000000) >> 8
        return [lo, hi]

    @property
    def dptr(self):
        return self.interpreter.dptr

    @property
    def sp(self) -> int:
        low = self.interpreter.memory[self.dptr]
        high = self.interpreter.memory[self.dptr+1]
        return (high << 8) | low

    def get_stack_contents(self, n) -> list:
        return self.interpreter.memory[max(0, self.dptr - n):self.dptr]

    def run_and_check(self, cases, source, check, init_vm=True):
        for case in cases:
            with self.subTest(values=case):
                self.setUp()
                exe = self.vm_source if init_vm else ""
                exe += self.assembler.assemble(source(case))
                self.interpreter.run(exe)
                check(case)

    def tearDown(self):
        print(f"Instructions: {len(self.interpreter.source)}")
        print(f"Cycles: {self.interpreter.cycles}")