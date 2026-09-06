from src.test.test_assembler import TestAssembler


class TestInternalMixin(TestAssembler):

    def test_mdr(self):
        values = (0, 1, 2, 5, 255, 256, 1000)
        bitwidths = (8, 16)
        cases = []
        for value in values:
            for bitwidth in bitwidths:
                cases.append((value, bitwidth))

        def source(case):
            return f"_MDR:{case[1]} {case[0]}"

        def check(case):
            self.assertEqual(case[0] * (1 if case[1] == 8 else 2), self.interpreter.dptr)
            self.assertEqual(0, self.assembler.stack_pointer)

        self.run_and_check(cases, source, check)

    def test_mdl(self):
        values = (0, 1, 2, 5, 255, 256, 1000)
        bitwidths = (8, 16)
        cases = []
        for value in values:
            for bitwidth in bitwidths:
                cases.append((value, bitwidth))

        def source(case):
            return f"""
                _MDR 1000
                _MDL:{case[1]} {case[0]}
            """

        def check(case):
            self.assertEqual(1000 - (case[0] * (1 if case[1] == 8 else 2)), self.interpreter.dptr)
            self.assertEqual(0, self.assembler.stack_pointer)

        self.run_and_check(cases, source, check)

    def test_add_8bit(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        def source(case):
            return f"_ADD {case}"

        def check(case):
            result = self.interpreter.memory[:4]
            self.assertEqual(case % 256, self.interpreter.memory[0], msg=result)
            self.assertEqual([0, 0, 0], self.interpreter.memory[1:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_mov_8bit(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        def source(case):
            return f"""
                _ADD:8 {case}
                _MOV:8 {2}
            """

        def check(case):
            expected = [0, 0, case % 256, 0]
            result = self.interpreter.memory[:4]
            self.assertEqual(expected, result)
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_mmv_8bit(self):
        cases = [(0, 1, 2), (1, 1, 2), (5, 4, 2), (255, 1, 2), (5, -1, 1), (5, -1, -2)]

        def source(case):
            return f"""
                _MDR 2
                _ADD:8 {case[0]}
                _MMV {case[1]} {case[2]}
            """

        def check(case):
            expected = [0] * 10
            expected[2] = 0
            expected[2+case[1]] = case[0]
            expected[2+case[2]] = case[0]
            result = self.interpreter.memory[:10]
            self.assertEqual(expected, result)
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(2, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_mov_16(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        def source(case):
            return f"""
                _ADD:16 {case}
                _MOV:16 {4}
                _MDR:8 {4}
                _MOV:16 {-2}
                _MDL:8 {2}
            """

        def check(case):
            expected = [0, 0] + self.to16bit(case) + [0, 0]
            result = self.interpreter.memory[:6]
            self.assertEqual(expected, result)
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(2, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_add_16bit(self):
        cases = [0, 1, 5, 255, 256, 3000, 65535, 65536, 65540]

        def source(case):
            return f"""
                _SET:16 260
                _ADD:16 {case}
            """

        def check(case):
            memory = self.interpreter.memory
            self.assertEqual(self.to16bit(260+case) + [0, 0], memory[:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_sub_8bit(self):
        cases = [
            (1, 0), (5, 0), (255, 0), (65535, 0),
            (1, 1), (5, 1), (5, 3), (5, 5), (255, 255),
            (257, 1), (257, 5), (3000, 2000), (65535, 2),
            (0, 1), (0, 5), (5, 10), (255, 256)
        ]

        def source(case):
            return f"""
                _ADD {case[0]}
                _SUB {case[1]}
            """

        def check(case):
            memory = self.interpreter.memory
            self.assertEqual((case[0] - case[1]) % 256, memory[0])
            self.assertEqual([0, 0, 0], memory[1:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_sub_16bit(self):
        cases = [
            (1, 0), (5, 0), (255, 0), (65535, 0),
            (1, 1), (5, 1), (5, 3), (5, 5), (255, 255),
            (257, 1), (257, 5), (3000, 2000), (65535, 2),
            (0, 1), (0, 5), (5, 10), (255, 256)
        ]

        def source(case):
            return f"""
                _ADD:16 {case[0]}
                _SUB:16 {case[1]}
            """

        def check(case):
            memory = self.interpreter.memory
            self.assertEqual(self.to16bit(case[0]-case[1]) + [0, 0], memory[:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_raw(self):
        cases = ("+", ">>+", "[-]", "++ - +")

        for case in cases:
            with self.subTest(case=case):
                exe = self.assembler.assemble(f"""
                    _RAW "{case}"
                """)
                self.assertEqual(case, exe)

    def test_hlt(self):
        cases = [()]

        def source(case):
            return f"""
                _ADD 2
                _JFZ
                    _HLT
                    _SUB 2
                _JBN
            """

        def check(case):
            self.assertEqual([2], self.interpreter.memory[0:1])
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_set_8bit(self):
        cases = [
            (1, 0), (5, 0), (255, 0), (65535, 0),
            (1, 1), (5, 1), (5, 3), (5, 5), (255, 255),
            (257, 1), (257, 5), (3000, 2000), (65535, 2),
            (0, 1), (0, 5), (5, 10), (255, 256)
        ]

        def source(case):
            return f"""
                _ADD {case[0]}
                _SET {case[1]}
            """

        def check(case):
            memory = self.interpreter.memory
            self.assertEqual(case[1] % 256, memory[0])
            self.assertEqual([0, 0, 0], memory[1:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_set_16bit(self):
        cases = [
            (1, 0), (5, 0), (255, 0), (65535, 0),
            (1, 1), (5, 1), (5, 3), (5, 5), (255, 255),
            (257, 1), (257, 5), (3000, 2000), (65535, 2),
            (0, 1), (0, 5), (5, 10), (255, 256), (5, 65535)
        ]

        def source(case):
            return f"""
                _ADD:16 {case[0]}
                _SET:16 {case[1]}
            """

        def check(case):
            memory = self.interpreter.memory
            self.assertEqual(self.to16bit(case[1]) + [0, 0], memory[:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_cpy_8(self):
        cases = [
            (0, 1, 2), (5, 1, 2), (255, 1, 2), (255, 20, 10),
            (5, -1, -3)
        ]

        def source(case):
            return f"""
                _MDR 5
                _ADD:8 {case[0]}
                _CPY:8 {case[1]} {case[2]}
            """

        def check(case):
            expected = [0] * 30
            expected[5] = case[0]
            expected[5+case[1]] = case[0]
            self.assertEqual(self.interpreter.memory[:30], expected)
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(5, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_cpy_16(self):
        cases = [
            (0, 2, 4), (5, 2, 4), (2557, 2, 4), (2558, 20, 10)
        ]

        def source(case):
            return f"""
                _ADD:16 {case[0]}
                _CPY:16 {case[1]} {case[2]}
            """

        def check(case):
            i = self.to16bit(case[0])
            expected = [0] * 30
            expected[0] = i[0]
            expected[1] = i[1]
            expected[case[1]] = i[0]
            expected[case[1]+1] = i[1]
            self.assertEqual(self.interpreter.memory[:30], expected)
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)