from src.test.test_assembler import TestAssembler


class TestMemoryMixin(TestAssembler):

    def test_push_top8_immediate8(self):

        cases = [(0, 0), (0, 1), (1, 0), (5, 5), (255, 0), (0, 255), (255, 255)]

        def source(case):
            return f"""
                PUSH @top:8 {case[0]}:8
                PUSH @top:8 {case[1]}:8
            """

        def check(case):
            self.assertStackContents(list(case), 2)

        self.run_and_check(cases, source, check)

    def test_push_top16_immediate16(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 5), (255, 0), (0, 255), (255, 255),
                 (0, 256), (256, 0), (256, 256), (65534, 1), (65535, 65535)]

        def source(case):
            return f"""
                PUSH @top:16 {case[0]}:16
                PUSH @top:16 {case[1]}:16
            """

        def check(case):
            self.assertStackContents(self.to16bit(case[0]) + self.to16bit(case[1]), 8)

        self.run_and_check(cases, source, check)

    def test_push_top8_direct8(self):
        cases = [(0, 0, 0), (1, 0, 0), (5, 5, 5), (255, 0, 0), (0, 0, 255), (255, 255, 255)]

        def source(case):
            self.assembler.vtable["a"] = 1
            return f"""
                PUSH @top {case[0]}:8
                PUSH @top {case[1]}:8
                PUSH @top {case[2]}:8
                PUSH @top @0
                PUSH @top @a
                PUSH @top @1[1]
            """

        def check(case):
            self.assertStackContents(list(case + case), 6)

        self.run_and_check(cases, source, check)

    def test_push_top8_top8(self):
        cases = [0, 1, 2, 255]

        def source(case):
            return f"""
                PUSH @top:8 {case}:8
                PUSH @top:8 @top:8
            """

        def check(case):
            self.assertStackContents([case] + [case], 2)

        self.run_and_check(cases, source, check)

    def test_push_top16_top16(self):
        cases = [0, 1, 2, 255, 65535]

        def source(case):
            return f"""
                PUSH @top:16 {case}:16
                PUSH @top:16 @top:16
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
                ALOC a 1:16
                ALOC b 1:16
                PUSH @a:16 {255}
                PUSH @b:16 {0}
                PUSH @a:16 {case}
                PUSH @b:16 {case+1}
            """

        def check(case):
            self.assertStackContents(self.to16bit(case) + self.to16bit(case+1), 8)

        self.run_and_check(cases, source, check)

    def test_swap_top8_top8(self):
        cases = [(0, 0), (0, 1), (1, 0), (5, 10), (255, 0), (0, 255), (255, 255)]

        def source(case):
            return f"""
                PUSH @top:8 {case[0]}:8
                PUSH @top:8 {case[1]}:8
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
                PUSH @top:16 {case}
                POPV @top:16
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