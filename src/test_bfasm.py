from unittest import TestCase

from src.bfasm import State
from src.interpreter import Interpreter


class TestBfasmInstructions(TestCase):
    def test_mov(self):
        state = State()
        self.assertEqual('>', state.assemble('_MOV 1'))
        self.assertEqual('>>>>>', state.assemble('_MOV 5'))
        self.assertEqual('<', state.assemble('_MOV -1'))
        self.assertEqual('<<<<<', state.assemble('_MOV -5'))
        self.assertEqual('', state.assemble('_MOV 0'))
        self.assertRaises(ValueError, lambda: state.assemble('_MOV $x'))

    def test_add(self):
        state = State()
        self.assertEqual('+', state.assemble('_ADD 1'))
        self.assertEqual('+++++', state.assemble('_ADD 5'))
        self.assertEqual('-', state.assemble('_ADD -1'))
        self.assertEqual('-----', state.assemble('_ADD -5'))
        self.assertEqual('', state.assemble('_ADD 0'))
        self.assertRaises(ValueError, lambda: state.assemble('_ADD $x'))

    def test_sub(self):
        state = State()
        self.assertEqual('-', state.assemble('_SUB 1'))
        self.assertEqual('-----', state.assemble('_SUB 5'))
        self.assertEqual('+', state.assemble('_SUB -1'))
        self.assertEqual('+++++', state.assemble('_SUB -5'))
        self.assertEqual('', state.assemble('_SUB 0'))
        self.assertRaises(ValueError, lambda: state.assemble('_SUB $x'))

    def test_res(self):
        state = State()
        self.assertEqual('[-]', state.assemble('_RES'))

    def test_seti(self):
        state = State()
        state.aloc('$n', 3)
        state.aloc('$m', 1)
        source = state.assemble("SETI $m 5")
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertEqual(0, interpreter.dptr)
        self.assertEqual(255, state.stackpointer)
        self.assertEqual(5, interpreter.memory[3])

    def test_stor(self):
        state = State()
        source = state.assemble(f"""STOR 10""")
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertEqual(0, interpreter.dptr)
        self.assertEqual(256, state.stackpointer)
        self.assertEqual(10, interpreter.memory[255])

    def test_push(self):
        state = State()
        state.aloc('$n', 1)
        source = state.assemble(f"""
            SETI $n 5
            PUSH $n
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertEqual(0, interpreter.dptr)
        self.assertEqual(256, state.stackpointer)
        self.assertEqual(5, interpreter.memory[255])
        self.assertEqual(0, interpreter.memory[256])
        self.assertEqual(5, interpreter.memory[0])

    def test_popn(self):
        state = State()
        source = state.assemble("""
            STOR 10
            POPN
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertEqual(0, interpreter.dptr)
        self.assertEqual(0, interpreter.memory[255])
        self.assertEqual(255, state.stackpointer)

    def test_pops(self):
        state = State()
        state.aloc("$n", 1)
        source = state.assemble("""
            STOR 10
            POPS $n
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertEqual(0, interpreter.dptr)
        self.assertEqual(0, interpreter.memory[255])
        self.assertEqual(255, state.stackpointer)
        self.assertEqual(10, interpreter.memory[0])

    def test_adda(self):
        state = State()
        state.aloc("$n", 1)
        state.aloc("$m", 1)
        source = state.assemble("""
            SETI $n 10
            SETI $m 5
            ADDA $n $m
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertDataPointerZero(interpreter)
        self.assertStackIsEmpty(state, interpreter)
        self.assertEqual(15, interpreter.memory[0])
        self.assertEqual(5, interpreter.memory[1])

    def test_adda_n_n(self):
        state = State()
        state.aloc("$n", 1)
        source = state.assemble("""
            SETI $n 10
            ADDA $n $n
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertDataPointerZero(interpreter)
        self.assertStackIsEmpty(state, interpreter)
        self.assertEqual(20, interpreter.memory[0])

    def test_copy(self):
        state = State()
        state.aloc("$n", 1)
        state.aloc("$m", 1)
        source = state.assemble("""
            SETI $m 10
            COPY $n $m
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertDataPointerZero(interpreter)
        self.assertStackIsEmpty(state, interpreter)
        self.assertEqual(10, interpreter.memory[0])
        self.assertEqual(10, interpreter.memory[1])

    def test_mult(self):
        state = State()
        state.aloc("$n", 1)
        source = state.assemble("""
            SETI $n 50
            MULT $n 5
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertDataPointerZero(interpreter)
        self.assertStackIsEmpty(state, interpreter)
        self.assertEqual(250, interpreter.memory[0])

    def test_mult_0(self):
        state = State()
        state.aloc("$n", 1)
        source = state.assemble("""
            SETI $n 50
            MULT $n 0
        """)
        interpreter = Interpreter(source)
        interpreter.run()
        self.assertDataPointerZero(interpreter)
        self.assertStackIsEmpty(state, interpreter)
        self.assertEqual(0, interpreter.memory[0])

    def assertDataPointerZero(self, interpreter):
        self.assertEqual(0, interpreter.dptr)

    def assertStackIsEmpty(self, state, interpreter):
        self.assertEqual(255, state.stackpointer)
        self.assertEqual(0, interpreter.memory[state.stackpointer])