import unittest
from spx.utils import seed_state
from spx.wots import *
from spx.address import WOTSAddress
import os


class TestWOTS(unittest.TestCase):
    def setUp(self):
        # Setup common test values
        self.sk_seed = bytearray(i for i in range(SPX_N))
        self.pub_seed = bytearray(i for i in range(SPX_N))
        self.addr = WOTSAddress()
        self.msg = bytearray(i for i in range(SPX_N))  # Random test message

    def test_wots_gen_pk(self):
        seed_state(self.pub_seed)
        pk = wots_gen_pk(self.sk_seed, self.pub_seed, self.addr)
        print(pk.hex())


if __name__ == "__main__":
    unittest.main()
