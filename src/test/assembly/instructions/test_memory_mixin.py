from src.test.test_assembler import TestAssembler


class TestMemoryMixin(TestAssembler):

    def test_push_16_top_imm(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 5), (255, 0), (0, 255), (255, 255),
                 (0, 256), (256, 0), (256, 256), (65534, 1), (65535, 65535)]

        def source(case):
            return f"""
                PUSH:16 @top {case[0]}
                PUSH:16 @top {case[1]}
            """

        def check(case):
            self.assertStackContents(self.to16bit(case[0]) + self.to16bit(case[1]), 4)

        self.run_and_check(cases, source, check)

    def test_push_16_addr_imm(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        def source(case):
            return f"""
                ALOC:16 a 1
                ALOC:16 b 1
                PUSH:16 @a {255}
                PUSH:16 @b {0}
                PUSH:16 @a {case}
                PUSH:16 @b {case+1}
            """

        def check(case):
            expected = self.to16bit(case) + self.to16bit(case + 1)
            self.assertStackContents(expected, 4)

        self.run_and_check(cases, source, check)

    def test_push_16_top_addr(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        def source(case):
            return f"""
                ALOC:16 a 1
                PUSH:16 @a {case}
                PUSH:16 @top {5}
                PUSH:16 @top @a
            """

        def check(case):
            expected = self.to16bit(case) + [5, 0] + self.to16bit(case)
            self.assertStackContents(expected, 6)

        self.run_and_check(cases, source, check)

    def test_push_8_top_address(self):
        cases = [(0, 0, 0), (1, 0, 0), (5, 5, 5), (255, 0, 0), (0, 0, 255), (255, 255, 255), (1, 2, 3)]

        def source(case):
            self.assembler.vtable["a"] = 1
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                PUSH @top {case[2]}
                PUSH @top @0
                PUSH @top @a
                PUSH @top @2
            """

        def check(case):
            self.assertStackContents(list(case + case), 6)

        self.run_and_check(cases, source, check)

    def test_push_top8_top8(self):
        cases = [0, 1, 2, 255]

        def source(case):
            return f"""
                PUSH @top {case}
                PUSH @top @top
            """

        def check(case):
            self.assertStackContents([case] + [case], 2)

        self.run_and_check(cases, source, check)

    def test_push_16_top_top(self):
        cases = [0, 1, 2, 255, 65535]

        def source(case):
            return f"""
                PUSH:16 @top {case}
                PUSH:16 @top @top
            """

        def check(case):
            self.assertStackContents(self.to16bit(case) + self.to16bit(case), 4)

        self.run_and_check(cases, source, check)

    def test_push_8_address_immediate(self):
        cases = [0, 1, 5, 254, 255, 256, 3000]

        def source(case):
            return f"""
                ALOC a 1
                ALOC b 1
                PUSH @a {255}
                PUSH @b {0}
                PUSH @a {case}
                PUSH @b {case+1}
            """

        def check(case):
            self.assertStackContents([case % 256, (case+1) % 256], 2)

        self.run_and_check(cases, source, check)

    def test_push_direct16_immediate(self):
        cases = [0, 1, 5, 254, 255, 256, 3000, 65535, 65536]

        def source(case):
            return f"""
                ALOC:16 a 1
                ALOC:16 b 1
                PUSH:16 @a {255}
                PUSH:16 @b {0}
                PUSH:16 @a {case}
                PUSH:16 @b {case+1}
            """

        def check(case):
            self.assertStackContents(self.to16bit(case) + self.to16bit(case+1), 8)

        self.run_and_check(cases, source, check)

    def test_push_top8_symbol8(self):
        cases = [0]

        def source(case):
            return f"""
                ALOC a 1
                ALOC b 1
                PUSH @top &a
                PUSH @top &b
                PUSH @top 5
            """

        def check(case):
            self.assertStackContents([0, 1, 5], 5)

        self.run_and_check(cases, source, check)

    def test_push_8_address_string(self):
        cases = ["", "a", "abc", "aaaaaaaaaaaaa"]

        def source(case):
            return f"""
                ALOC a {len(case) + 1}
                PUSH @a "{case}"
            """

        def check(case):
            expected = [ord(c) for c in case] + [0]
            self.assertStackContents(expected, len(case)+1)

        self.run_and_check(cases, source, check)

    def test_swap_top8_top8(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 10), (255, 0), (0, 255), (255, 255)]

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                SWAP @top @top
            """

        def check(case):
            self.assertStackContents(list(case[::-1]), 2)

        self.run_and_check(cases, source, check)

    def test_swap_16_top_top(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 10), (255, 0), (0, 255), (255, 255),
                 (3000, 6), (6, 3000), (65536, 0)]

        def source(case):
            return f"""
                PUSH:16 @top {case[0]}
                PUSH:16 @top {case[1]}
                SWAP:16 @top @top
            """

        def check(case):
            self.assertStackContents(self.to16bit(case[1]) + self.to16bit(case[0]), 4)

        self.run_and_check(cases, source, check)

    def test_popv_top8(self):
        cases = [0, 1, 2, 255]

        def source(case):
            return f"""
                PUSH @top {case}
                POPV @top
            """

        def check(case):
            self.assertStackContents([], 0)

        self.run_and_check(cases, source, check)

    def test_popv_16_top(self):
        cases = [0, 1, 2, 255, 3000, 65535]

        def source(case):
            return f"""
                PUSH:16 @top 5
                PUSH:16 @top {case}
                POPV:16 @top
            """

        def check(case):
            self.assertStackContents([5, 0], 2)

        self.run_and_check(cases, source, check)

    def test_popv_8_address_top(self):
        cases = [0, 1, 2, 255, 3000, 65535]

        def source(case):
            return f"""
                ALOC a 1
                ALOC b 1
                ALOC c 1
                PUSH @b 5
                PUSH @top {case}
                POPV @b @top
            """

        def check(case):
            self.assertStackContents([0, case % 256, 0], 3)

        self.run_and_check(cases, source, check)

    def test_popv_16_address_top(self):
        cases = [0, 1, 5, 255, 3000, 65535]

        def source(case):
            return f"""
                 ALOC:16 a 1
                 ALOC:16 b 1
                 PUSH:16 @b 258
                 PUSH:16 @top {case}
                 POPV:16 @b @top
             """

        def check(case):
            expected = [0, 0] + self.to16bit(case)
            self.assertStackContents(expected, 4)

        self.run_and_check(cases, source, check)

    def test_geti_8_top_top(self):
        cases = [0, 1, 2, 3, 4]

        def source(case):
            return f"""
                PUSH @top 10
                PUSH @top 11
                PUSH @top 12
                PUSH @top 13
                PUSH @top 14
                PUSH @top {case}
                GETI @top @top
            """

        def check(case):
            self.assertStackContents([10, 11, 12, 13, 14, case+10], 6)

        self.run_and_check(cases, source, check)

    def test_geti_16_top_top(self):
        cases = [250]

        def source(case):
            bfasm = ""

            # Fill addresses 0-300 with that address as the value
            for i in range(150):
                bfasm += f"PUSH:16 @top {i * 2}\n"

            return bfasm + f"""
                PUSH:16 @top {case}
                GETI:16 @top @top
            """

        def check(case):
            expected = [34, 1, 36, 1, 38, 1, 40, 1, 42, 1] + self.to16bit(case)
            self.assertStackContents(expected, 302)

        self.run_and_check(cases, source, check)

    def test_seti_top8_top8(self):
        cases = [0, 1, 2, 3, 4]

        def source(case):
            return f"""
                PUSH @top 1
                PUSH @top 2
                PUSH @top 3
                PUSH @top 4
                PUSH @top 5
                PUSH @top 10
                PUSH @top {case}
                SETI @top @top
            """

        def check(case):
            expected = [1, 2, 3, 4, 5]
            expected[case] = 10
            self.assertStackContents(expected, 5)

        self.run_and_check(cases, source, check)