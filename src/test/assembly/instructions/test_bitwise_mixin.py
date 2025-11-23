from src.test.test_assembler import TestAssembler


class TestBitwiseMixin(TestAssembler):

    def test_lsft8_top_top_immediate(self):
        cases = [[10, 2], [1, 40], [1, 1], [1, 5], [1, 255], [5, 5],
                 [30, 3], [30, 30], [255, 1], [255, 255]]
        cases.extend([c[::-1] for c in cases if c[0] != c[1]])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                LSFT @top @top {case[1]}
            """

        def check(case):
            self.assertStackContents([(case[0] << case[1]) % 256], 1)

        self.run_and_check(cases, source, check)

    def test_rsft8_top_top_immediate(self):
        cases = [[0, 1], [0, 2], [10, 2], [1, 4], [1, 1], [1, 5], [1, 255], [5, 5],
                 [30, 3], [30, 30], [255, 1], [255, 255],
                 [8, 1], [15, 3]]
        cases.extend([c[::-1] for c in cases if c[0] != c[1]])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                RSFT @top @top {case[1]}
            """

        def check(case):
            self.assertStackContents([case[0] >> case[1]], 1)

        self.run_and_check(cases, source, check)

    def test_band8_top_top_top(self):
        cases = [[0, 1], [0, 2], [10, 2], [1, 4], [1, 1], [1, 5], [1, 255], [5, 5],
                 [30, 3], [30, 30], [255, 1], [255, 255],
                 [8, 1], [15, 3]]
        cases.extend([c[::-1] for c in cases if c[0] != c[1]])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                BAND @top @top @top
            """

        def check(case):
            self.assertStackContents([case[0] & case[1]], 1)

        self.run_and_check(cases, source, check)