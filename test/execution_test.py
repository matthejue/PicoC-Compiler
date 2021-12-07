#!/usr/bin/python

import unittest
from testing_helpers import UsefullTools


class TestPrograms(unittest.TestCase, UsefullTools):
    def test_gcd(self, ):
        self.set_everything_up_for_testing_program_file(
            "gcd", "./test/gcd.picoc")

    def uebungsblatt_5_aufgabe_3(self, ):
        self.set_everything_up_for_testing_program_file(
            "uebungsblatt_5_aufgabe_3", "./test/uebungsblatt_5_aufgabe_3.picoc")

    def uebungsblatt_6_aufgabe_1(self, ):
        self.set_everything_up_for_testing_program_file(
            "uebungsblatt_6_aufgabe_1", "./test/uebungsblatt_6_aufgabe_1.picoc")


if __name__ == '__main__':
    unittest.main()
