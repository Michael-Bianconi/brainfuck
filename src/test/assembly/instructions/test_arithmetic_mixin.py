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

    def test_plus_top16_top16_top16(self):
        cases = [
            (0, 0), (0, 1), (5, 5), (2, 253), (1, 255), (256, 10), (1000, 2000), (65534, 1),
            (6553, 1), (1, 6553), (30000, 5), (5, 30000), (65530, 5), (5, 65530), (65535, 2), (2, 65535)
        ]

        def source(case):
            return f"""
                PUSH @top:16 {case[0]}
                PUSH @top:16 {case[1]}
                PLUS @top:16 @top:16 @top:16
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
                PUSH @top:16 {case[0]}
                PUSH @top:16 {case[1]}
                SUBT @top:16 @top:16 @top:16
            """

        def check(case):
            self.assertStackContents(self.to16bit(case[0]-case[1]), 4)

        self.run_and_check(cases, source, check)