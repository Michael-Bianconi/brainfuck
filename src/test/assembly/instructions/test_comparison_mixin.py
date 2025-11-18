from src.test.test_assembler import TestAssembler


class TestComparisonMixin(TestAssembler):

    def test_land_8_top_top_top(self):
        cases = [[0, 0], [1, 0], [5, 0], [255, 0], [1, 1], [5, 5], [255, 255]]
        cases.extend([x[::-1] for x in cases])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                LAND @top @top @top
            """

        def check(case):
            self.assertStackContents([(case[0] > 0 and case[1] > 0)], 1)

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