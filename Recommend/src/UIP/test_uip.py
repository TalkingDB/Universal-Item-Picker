# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="Karan S. Sisodia"
__email__="karansinghsisodia@gmail.com"
__date__ ="$Sep 19, 2014 11:30:42 AM$"

import unittest


class TestUIP(unittest.TestCase):

    def setUp(self):
        pass

    def test_numbers_3_4(self):
        self.assertEqual( 12, 12)

    def test_strings_a_3(self):
        self.assertEqual( 'aaa', 'aaa')

if __name__ == '__main__':
    unittest.main()
