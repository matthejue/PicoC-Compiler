#!/usr/bin/python

import unittest
from testing_helpers import UsefullTools


class TestPrograms(unittest.TestCase, UsefullTools):
    def test_gcd(self, ):
        self.set_everything_up_for_testing_program_file(
            "gcd", "./test/gcd.picoc")


if __name__ == '__main__':
    unittest.main()
