import unittest
from spx.wots import *
from spx.address import WOTSAddress
import os


class TestWOTS(unittest.TestCase):
    def setUp(self):
        # Setup common test values
        self.sk_seed = os.urandom(SPX_N)
        self.pub_seed = os.urandom(SPX_N)
        self.addr = WOTSAddress()
        self.msg = os.urandom(SPX_N)  # Random test message

    def test_gen_chain_basic(self):
        input_data = os.urandom(SPX_N)
        start = 0
        steps = 1
        result = gen_chain(input_data, start, steps, self.pub_seed, self.addr)
        self.assertEqual(len(result), SPX_N)
        
if __name__ == '__main__':
    unittest.main()
