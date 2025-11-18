from src.test.test_assembler import TestAssembler


class TestInternalMixin(TestAssembler):

    def test_rit(self):
        values = (0, 1, 2, 5, 255, 256, 1000)
        bitwidths = (8, 16)
        cases = []
        for value in values:
            for bitwidth in bitwidths:
                cases.append((value, bitwidth))

        def source(case):
            return f"_RIT:{case[1]} {case[0]}"

        def check(case):
            self.assertEqual(case[0] * (1 if case[1] == 8 else 4), self.interpreter.dptr)
            self.assertEqual(0, self.assembler.stack_pointer)

        self.run_and_check(cases, source, check)

    def test_lft(self):
        values = (0, 1, 2, 5, 255, 256, 1000)
        bitwidths = (8, 16)
        cases = []
        for value in values:
            for bitwidth in bitwidths:
                cases.append((value, bitwidth))

        def source(case):
            return f"""
                _RIT 1000
                _LFT:{case[1]} {case[0]}
            """

        def check(case):
            self.assertEqual(1000 - (case[0] * (1 if case[1] == 8 else 4)), self.interpreter.dptr)
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

    def test_add_16bit(self):
        cases = [0, 1, 5, 255, 256, 3000, 65535, 65536, 65540]

        def source(case):
            return f"_ADD:16 {case}"

        def check(case):
            memory = self.interpreter.memory
            self.assertEqual(self.to16bit(case), memory[:4])
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
            self.assertEqual(self.to16bit(case[0]-case[1]), memory[:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)

    def test_raw(self):
        cases = ("+", ">>+", "[-]", "++ - +")

        for case in cases:
            with self.subTest(case=case):
                exe = self.assembler.assemble(f"_RAW {case}")
                self.assertEqual(''.join(case.split()), exe)

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
            self.assertEqual(self.to16bit(case[1]), memory[:4])
            self.assertEqual(0, self.assembler.stack_pointer)
            self.assertEqual(0, self.interpreter.dptr)

        self.run_and_check(cases, source, check)