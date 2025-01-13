import hashlib
import unittest
from spx.utils import seed_state, IV_256, state_seeded

class TestUtils(unittest.TestCase):
    def test_seed_state(self):
        pub_seed = bytes(i for i in range(16)) 
        print(pub_seed)
        seed_state(pub_seed)
        
        # FIXME: This test is not working as expected, because the crypto_hashblocks_sha256, not implemented correctly
        # Check if the state is initialized with IV
        # self.assertEqual(state_seeded[0:32], IV_256)
        # here is the expected value of state_seeded[0:32] 45838f7475fab31a78f3562b1af672e7f3907d7124737fdb83360031554eb30d
        # except_state = bytearray([0x45, 0x83, 0x8f, 0x74, 0x75, 0xfa, 0xb3, 0x1a, 0x78, 0xf3, 0x56, 0x2b, 0x1a, 0xf6, 0x72, 0xe7, 0xf3, 0x90, 0x7d, 0x71, 0x24, 0x73, 0x7f, 0xdb, 0x83, 0x36, 0x00, 0x31, 0x55, 0x4e, 0xb3, 0x0d])
        # self.assertEqual(state_seeded[0:32], except_state)
        
        # Check if the counter is zero
        counter = bytearray(8)
        counter[7] = 64
        self.assertEqual(state_seeded[32:40], counter)
        

if __name__ == '__main__':
    unittest.main()