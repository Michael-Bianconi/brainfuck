from unittest import TestCase

from src.bfasm import State
from src.interpreter import Interpreter


class TestBfasmInstructions(TestCase):

    def setUp(self) -> None:
        self.stackaddr = 4
        self.state = State(stackaddr=self.stackaddr)
        self.interpreter = Interpreter()

    def test_mov(self):
        self.assertEqual('>', self.state.assemble('_MOV 1'))
        self.assertEqual('>>>>>', self.state.assemble('_MOV 5'))
        self.assertEqual('<', self.state.assemble('_MOV -1'))
        self.assertEqual('<<<<<', self.state.assemble('_MOV -5'))
        self.assertEqual('', self.state.assemble('_MOV 0'))
        self.assertRaises(ValueError, lambda: self.state.assemble('_MOV $x'))

    def test_add(self):
        self.assertEqual('+', self.state.assemble('_ADD 1'))
        self.assertEqual('+++++', self.state.assemble('_ADD 5'))
        self.assertEqual('-', self.state.assemble('_ADD -1'))
        self.assertEqual('-----', self.state.assemble('_ADD -5'))
        self.assertEqual('', self.state.assemble('_ADD 0'))
        self.assertRaises(ValueError, lambda: self.state.assemble('_ADD $x'))

    def test_sub(self):
        self.assertEqual('-', self.state.assemble('_SUB 1'))
        self.assertEqual('-----', self.state.assemble('_SUB 5'))
        self.assertEqual('+', self.state.assemble('_SUB -1'))
        self.assertEqual('+++++', self.state.assemble('_SUB -5'))
        self.assertEqual('', self.state.assemble('_SUB 0'))
        self.assertRaises(ValueError, lambda: self.state.assemble('_SUB $x'))

    def test_res(self):
        self.assertEqual('[-]', self.state.assemble('_RES'))

    def test_seti(self):
        self.state.aloc('$n', 2)
        self.state.aloc('$m', 1)
        source = self.state.assemble("SETI $m 5")
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(5, "$m")

    def test_stor(self):
        source = self.state.assemble("STOR 10")

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackEqual(10, 0)
        self.assertStackEqual(0, 1)

    def test_push(self):
        self.state.aloc('$n', 1)
        source = self.state.assemble(f"""
            SETI $n 5
            PUSH $n
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertEqual(self.stackaddr + 1, self.state.stackpointer)
        self.assertStackEqual(5, 0)
        self.assertStackEqual(0, 1)
        self.assertVarEqual(5, "$n")

    def test_popn(self):
        source = self.state.assemble("""
            STOR 10
            POPN
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()

    def test_pops(self):
        self.state.aloc("$n", 1)
        source = self.state.assemble("""
            STOR 10
            POPS $n
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(10, "$n")

    def test_adda(self):
        self.state.aloc("$n", 1)
        self.state.aloc("$m", 1)
        source = self.state.assemble("""
            SETI $n 10
            SETI $m 5
            ADDA $n $m
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(15, "$n")
        self.assertVarEqual(5, "$m")

    def test_adda_n_n(self):
        self.state.aloc("$n", 1)
        source = self.state.assemble("""
            SETI $n 10
            ADDA $n $n
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(20, "$n")

    def test_copy(self):
        self.state.aloc("$n", 1)
        self.state.aloc("$m", 1)
        source = self.state.assemble("""
            SETI $m 10
            COPY $n $m
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(10, "$n")
        self.assertVarEqual(10, "$m")

    def test_mult(self):
        self.state.aloc("$n", 1)
        source = self.state.assemble("""
            SETI $n 50
            MULT $n 5
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(250, "$n")

    def test_mult_0(self):
        self.state.aloc("$n", 1)
        source = self.state.assemble("""
            SETI $n 50
            MULT $n 0
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(0, "$n")

    def test_lnot_1(self):
        
        self.state.aloc("$n", 1)
        self.state.aloc("$m", 1)
        source = self.state.assemble("""
            SETI $n 4
            SETI $m 2
            LNOT $n $m
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(0, "$n")
        self.assertVarEqual(2, "$m")

    def test_lnot_2(self):
        self.state.aloc("$n", 1)
        self.state.aloc("$m", 1)
        source = self.state.assemble("""
            SETI $n 4
            SETI $m 0
            LNOT $n $m
        """)

        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(1, "$n")
        self.assertVarEqual(0, "$m")

    def test_lnot_3(self):
        self.state.aloc("$n", 1)
        source = self.state.assemble("""
            SETI $n 4
            LNOT $n $n
        """)
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(0, "$n")

    def test_lnot_4(self):
        source = self.state.assemble("""
            ALOC $n 1
            SETI $n 0
            LNOT $n $n
        """)
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(1, "$n")

    def test_call(self):
        source = self.state.assemble("""
            .FUNCTION add3
                ADDI $n 2
                ADDI $n 1
            .RETURN
            ALOC $n 1
            CALL add3
            CALL add3
            CALL add3
        """)
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(9, "$n")

    def test_jinz_1(self):
        source = self.state.assemble("""
            .FUNCTION add3
                ADDI $n 2
                ADDI $n 1
            .RETURN
            ALOC $n 1
            ALOC $m 1
            JINZ $m add3
        """)
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(0, "$n")
        self.assertVarEqual(0, "$m")

    def test_jinz_2(self):
        source = self.state.assemble("""
            .FUNCTION add3
                ADDI $n 2
                ADDI $n 1
            .RETURN

            ALOC $n 1
            ALOC $m 1
            SETI $m 10
            JINZ $m add3
        """)
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(3, "$n")
        self.assertVarEqual(10, "$m")

    def test_jiez_1(self):
        source = self.state.assemble("""
            .FUNCTION add3
                ADDI $n 2
                ADDI $n 1
            .RETURN

            ALOC $n 1
            ALOC $m 1
            JIEZ $m add3
        """)
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(3, "$n")
        self.assertVarEqual(0, "$m")

    def test_jiez_2(self):
        self.state.aloc("$n", 1)
        self.state.aloc("$m", 1)
        source = self.state.assemble("""
            .FUNCTION add3
                ADDI $n 2
                ADDI $n 1
            .RETURN

            SETI $m 10
            JIEZ $m add3
        """)
        self.interpreter.run(source)
        self.assertDataPointerZero()
        self.assertStackIsEmpty()
        self.assertVarEqual(0, "$n")
        self.assertVarEqual(10, "$m")

    def test_lshi_0(self):
        source = self.state.assemble("""
            ALOC $n 1
            SETI $n 1
            LSHI $n 0
        """)
        self.interpreter.run(source)
        self.assertVarEqual(1, "$n")

    def test_lshi_1(self):
        source = self.state.assemble("""
            ALOC $n 1
            SETI $n 1
            LSHI $n 1
        """)
        self.interpreter.run(source)
        self.assertVarEqual(2, "$n")

    def test_lshi_2(self):
        source = self.state.assemble("""
            ALOC $n 1
            SETI $n 1
            LSHI $n 1
        """)
        self.interpreter.run(source)
        self.assertVarEqual(2, "$n")

    def test_lshi_3(self):
        source = self.state.assemble("""
            ALOC $n 1
            SETI $n 1
            LSHI $n 8
        """)
        self.interpreter.run(source)
        self.assertVarEqual(0, "$n")

    def assertVarEqual(self, value, var):
        self.assertEqual(value, self.interpreter.memory[self.state.data[var]])

    def assertDataPointerZero(self):
        self.assertEqual(0, self.interpreter.dptr)

    def assertStackIsEmpty(self):
        self.assertEqual(self.stackaddr, self.state.stackpointer)
        self.assertEqual(0, self.interpreter.memory[self.state.stackpointer])

    def assertStackEqual(self, value, position):
        self.assertEqual(value, self.interpreter.memory[self.stackaddr + position])