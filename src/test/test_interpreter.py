from unittest import TestCase
import unittest.mock
import io

from src.interpreter import Interpreter


class TestInterpreter(TestCase):

    def test_012345(self):
        interpreter = Interpreter()
        output = self.capturestdout(interpreter, f"""
            {'+' * 48}.>
            {'+' * 49}.>
            {'+' * 50}.>
            {'+' * 51}.>
            {'+' * 52}.>
            {'+' * 53}.>
        """)
        self.assertListEqual([48,49,50,51,52,53], interpreter.memory[0:6])
        self.assertEqual("012345\n\n", output)

    def test_h(self):
        interpreter = Interpreter("++++++++[>+++++++++++++<-]>.")
        output = self.capturestdout(interpreter)
        self.assertListEqual([0,104], interpreter.memory[0:2])
        self.assertEqual("h\n\n", output)

    def test_helloworld(self):
        interpreter = Interpreter()
        output = self.capturestdout(interpreter, """
            >++++++++[<+++++++++>-]<.
            >++++[<+++++++>-]<+.
            +++++++..
            +++.
            >>++++++[<+++++++>-]<++.
            ------------.
            >++++++[<+++++++++>-]<+.
            <.
            +++.
            ------.
            --------.
            >>>++++[<++++++++>-]<+.
        """)
        self.assertEqual("Hello, World!\n\n", output)


    @unittest.mock.patch('sys.stdin.read', return_value='1')
    def test_read(self, mock_stdin):
        interpreter = Interpreter()
        output = self.capturestdout(interpreter, """,.""")
        self.assertEqual("1\n\n", output)


    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def capturestdout(self, interpreter, source, mock_stdout):
        interpreter.run(source)
        return mock_stdout.getvalue()
