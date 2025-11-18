from src.test.test_assembler import TestAssembler


class TestMemoryMixin(TestAssembler):

    def test_push_top8_immediate8(self):

        cases = [(0, 0), (0, 1), (1, 0), (5, 5), (255, 0), (0, 255), (255, 255)]

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
            """

        def check(case):
            self.assertStackContents(list(case), 2)

        self.run_and_check(cases, source, check)

    def test_push_top16_immediate16(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 5), (255, 0), (0, 255), (255, 255),
                 (0, 256), (256, 0), (256, 256), (65534, 1), (65535, 65535)]

        def source(case):
            return f"""
                PUSH:16 @top {case[0]}
                PUSH:16 @top {case[1]}
            """

        def check(case):
            self.assertStackContents(self.to16bit(case[0]) + self.to16bit(case[1]), 8)

        self.run_and_check(cases, source, check)

    def test_push_top8_address8(self):
        cases = [(0, 0, 0), (1, 0, 0), (5, 5, 5), (255, 0, 0), (0, 0, 255), (255, 255, 255)]

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

    def test_push_top16_top16(self):
        cases = [0, 1, 2, 255, 65535]

        def source(case):
            return f"""
                PUSH:16 @top {case}
                PUSH:16 @top @top
            """

        def check(case):
            self.assertStackContents(self.to16bit(case) + self.to16bit(case), 8)

        self.run_and_check(cases, source, check)

    def test_push_direct8_immediate(self):
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

    def test_popv_top16(self):
        cases = [0, 1, 2, 255, 3000, 65535]

        def source(case):
            return f"""
                PUSH:16 @top {case}
                POPV:16 @top
            """

        def check(case):
            self.assertStackContents([], 0)

        self.run_and_check(cases, source, check)

    def test_popv_direct8_top8(self):
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

    def test_geti_top8_top8(self):
        cases = [0, 1, 2, 3, 4]

        def source(case):
            return f"""
                PUSH @top 1
                PUSH @top 2
                PUSH @top 3
                PUSH @top 4
                PUSH @top 5
                PUSH @top {case}
                GETI @top @top
            """

        def check(case):
            self.assertStackContents([1, 2, 3, 4, 5, case+1], 6)

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