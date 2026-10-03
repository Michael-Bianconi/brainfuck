from src.test.test_assembler import TestAssembler


class TestPush(TestAssembler):

    def test_push_immediate(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 5), (255, 0), (0, 255), (255, 255),
                 (0, 256), (256, 0), (256, 256), (65534, 1), (65535, 65535)]

        def source(case):
            return f"""
                PUSH {case[0]}
                PUSH {case[1]}
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents(self.to16bit(case[0]) + self.to16bit(case[1]))

        self.run_and_check(cases, source, check)

    def test_push_register(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 5), (255, 0), (0, 255), (255, 255),
                 (0, 256), (256, 0), (256, 256), (65534, 1), (65535, 65535)]

        def source(case):
            return f"""
                PUSH {case[0]}
                PUSH {case[1]}
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents(self.to16bit(case[0]) + self.to16bit(case[1]))

        self.run_and_check(cases, source, check)

    def test_push_sp(self):
        cases = [0, 1, 2, 255, 65535]

        def source(case):
            return f"""
                PUSH {case}
                PUSH $sp
            """

        def check(case):
            self.assertRegisters({})
            self.assertDataPointerAlignsWithStackPointer(4)
            self.assertStackContents(self.to16bit(case) + self.to16bit(case))

        self.run_and_check(cases, source, check)