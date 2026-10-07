from src.test.test_assembler import TestAssembler


class TestPrnt(TestAssembler):

    def test_prnt_sp_imm(self):
        cases = ["", "Hello, world!"]

        def source(case):
            result = ""
            for c in case[::-1]:
                result += f"PUSH {ord(c)}\n"
            return result + f"""
                PRNT $sp {len(case)}
            """

        def check(case):
            self.assertStdout(case)
            self.assertDataPointerAlignsWithStackPointer(0)

        self.run_and_check(cases, source, check)

    def test_prnt_reg(self):
        cases = ["", "Hello, world!"]

        def source(case):
            location = self.prog_start - 100
            result = "_MDP -100\n"
            for c in case:
                result += f"_ADD {ord(c)}\n"
                result += f"_MDP 1\n"
            result += f"""
                _MDP {100 - (len(case))}
                LOAD $v1 {location}
                PRNT $v1
            """
            return result

        def check(case):
            self.assertStdout(case)
            self.assertDataPointerAlignsWithStackPointer(0)

        self.run_and_check(cases, source, check)