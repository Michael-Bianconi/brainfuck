from src.test.test_assembler import TestAssembler


class TestArithmeticMixin(TestAssembler):

    def test_plus_top8_top8_top8(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255)
        ]

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                PLUS @top @top @top
            """

        def check(case):
            self.assertStackContents([(case[0] + case[1]) % 256], 1)

        self.run_and_check(cases, source, check)

    def test_plus_top8_immediate8_top8(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255)
        ]

        def source(case):
            return f"""
                PUSH @top {case[1]}
                PLUS @top {case[0]} @top
            """

        def check(case):
            self.assertStackContents([(case[0] + case[1]) % 256], 1)

        self.run_and_check(cases, source, check)

    def test_plus_top8_top8_immediate8(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255)
        ]

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PLUS @top @top {case[1]}
            """

        def check(case):
            self.assertStackContents([(case[0] + case[1]) % 256], 1)

        self.run_and_check(cases, source, check)

    def test_plus_top16_top16_top16(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)
        ]

        def source(case):
            return f"""
                PUSH:16 @top {case[0]}
                PUSH:16 @top {case[1]}
                PLUS:16 @top @top @top
            """

        def check(case):
            self.assertStackContents(self.to16bit(sum(case)), 4)

        self.run_and_check(cases, source, check)

    def test_subt_top16_top16_top16(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)]

        def source(case):
            return f"""
                PUSH:16 @top {case[0]}
                PUSH:16 @top {case[1]}
                SUBT:16 @top @top @top
            """

        def check(case):
            self.assertStackContents(self.to16bit(case[0]-case[1]), 4)

        self.run_and_check(cases, source, check)

    def test_multiply_top8_top8_top8(self):
        cases = [[0, 0], [1, 0], [1, 1], [1, 5], [1, 255], [5, 5],
                 [30, 3], [30, 30], [255, 0], [255, 1], [255, 255]]
        cases.extend([c[::-1] for c in cases])

        def source(case):
            return f"""
                PUSH @top {case[0]}
                PUSH @top {case[1]}
                MULT @top @top @top
            """

        def check(case):
            self.assertStackContents([(case[0] * case[1]) % 256], 1)

        self.run_and_check(cases, source, check)