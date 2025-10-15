from unittest import TestCase
import unittest.mock
import io

from src.interpreter import Interpreter


class TestInterpreter(TestCase):

    def test_012345(self):
        interpreter = Interpreter(f"""
            {'+' * 48}.>
            {'+' * 49}.>
            {'+' * 50}.>
            {'+' * 51}.>
            {'+' * 52}.>
            {'+' * 53}.>
        """)
        output = self.capturestdout(interpreter)
        self.assertListEqual([48,49,50,51,52,53], interpreter.memory[0:6])
        self.assertEqual("012345\n\n", output)

    def test_h(self):
        interpreter = Interpreter("++++++++[>+++++++++++++<-]>.")
        output = self.capturestdout(interpreter)
        self.assertListEqual([0,104], interpreter.memory[0:2])
        self.assertEqual("h\n\n", output)

    def test_helloworld(self):
        interpreter = Interpreter("""
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
        output = self.capturestdout(interpreter)
        self.assertEqual("Hello, World!\n\n", output)

    def test_add32(self):
        interpreter = Interpreter("""
        +
        [<+>>>>>+<<<<-]<[>+<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[-
         >>+
         [<<+>>>>>+<<<-]<<[>>+<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[-
          >>>+
          [<<<+>>>>>+<<-]<<<[>>>+<<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[-
           >>>>+<<<<
          ]
         ]
        ]>
        """ * 256)
        interpreter.run()
        self.assertListEqual([0, 0, 0, 1], interpreter.memory[:4])

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def capturestdout(self, interpreter, mock_stdout):
        interpreter.run()
        return mock_stdout.getvalue()

