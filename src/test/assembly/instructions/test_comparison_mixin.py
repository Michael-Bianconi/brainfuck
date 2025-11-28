from src.test.test_assembler import TestAssembler


class TestComparisonMixin(TestAssembler):

    def test_land_8_top_top_top(self):
        cases = [[0, 0], [1, 0], [5, 0], [255, 0], [1, 1], [5, 5], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH @top 1
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                LAND @top @top @top
            """

        def check(case):
            self.assertStackContents([1, (case[0] > 0 and case[1] > 0)], 2)

        self.run_and_check(cases, source, check)

    def test_loor_8_top_top_top(self):
        cases = [[0, 0], [1, 0], [5, 0], [255, 0], [1, 1], [5, 5], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                LOOR @top @top @top
            """

        def check(case):
            self.assertStackContents([(case[0] > 0 or case[1] > 0)], 1)

        self.run_and_check(cases, source, check)

    def test_lxor_8_top_top_top(self):
        cases = [[0, 0], [1, 0], [5, 0], [255, 0], [1, 1], [5, 5], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                LXOR @top @top @top
            """

        def check(case):
            self.assertStackContents([((case[0] > 0) ^ (case[1] > 0))], 1)

        self.run_and_check(cases, source, check)

    def test_lxnr_8_top_top_top(self):
        cases = [[0, 0], [1, 0], [5, 0], [255, 0], [1, 1], [5, 5], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                LXNR @top @top @top
            """

        def check(case):
            result = 1 if (((case[0] > 0) and (case[1] > 0)) or ((case[0] == 0) and (case[1] == 0))) else 0
            self.assertStackContents([result], 1)

        self.run_and_check(cases, source, check)

    def test_eqls8_top_top_top(self):

        cases = [[5, 5], [0, 5], [0, 0], [5, 4], [255, 4], [5, 255], [0, 255], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                EQLS @top @top @top
            """

        def check(case):
            self.assertStackContents([1 if case[0] == case[1] else 0], 1)

        self.run_and_check(cases, source, check)

    def test_eqls8_top_top_immediate(self):

        cases = [[5, 0],[0, 5], [0, 0], [5, 4], [255, 4], [5, 255], [0, 255], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                EQLS @top @top {case[1]}
            """

        def check(case):
            self.assertStackContents([1 if case[0] == case[1] else 0], 1)

        self.run_and_check(cases, source, check)

    def test_eqls16_top_top_top(self):

        cases = [[5, 5], [0, 5], [0, 0], [5, 4], [255, 4], [5, 255], [0, 255], [255, 255],
                 [0, 256], [0, 3000], [0, 65535], [256, 256, 65535]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH:16 @top {case[0]}
                PUSH:16 @top {case[1]}
                EQLS:8:16:16 @top @top @top
            """

        def check(case):
            self.assertStackContents([1 if case[0] == case[1] else 0], 1)

        self.run_and_check(cases, source, check)

    def test_less_8_top_top_top(self):
        cases = [[0, 0], [0, 1], [1, 1], [1, 5], [5, 255], [255, 255]]
        cases.extend([c[::-1] for c in cases if c[0] != c[1]])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                LESS @top @top @top
            """

        def check(case):
            self.assertStackContents([1 if case[0] < case[1] else 0], 1)

        self.run_and_check(cases, source, check)

    def test_logical_not(self):
        cases = [0, 1, 2, 5, 255]

        def source(case):
            return f"""
                PUSH @top {case}
                LNOT @top @top
            """

        def check(case):
            self.assertStackContents([0 if case > 0 else 1], 1)

        self.run_and_check(cases, source, check)

    def test_grtr_8_top_top_top(self):
        cases = [[0, 0], [0, 1], [1, 1], [1, 5], [5, 255], [255, 255]]
        cases.extend([c[::-1] for c in cases if c[0] != c[1]])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                GRTR @top @top @top
            """

        def check(case):
            self.assertStackContents([1 if case[0] > case[1] else 0], 1)

        self.run_and_check(cases, source, check)