import hashlib
import unittest
from spx.address import Address
from spx.utils import (
    seed_state,
    IV_256,
    state_seeded,
    thash,
    SPX_N,
    SPX_SHA256_ADDR_BYTES,
)


class TestUtils(unittest.TestCase):
    def test_seed_state(self):
        pub_seed = bytes(i for i in range(16))
        print(pub_seed)
        seed_state(pub_seed)

        # Check if the state is initialized with IV
        # self.assertEqual(state_seeded[0:32], IV_256)
        # here is the expected value of state_seeded[0:32] 45838f7475fab31a78f3562b1af672e7f3907d7124737fdb83360031554eb30d
        except_state = bytearray(
            [
                0x45,
                0x83,
                0x8F,
                0x74,
                0x75,
                0xFA,
                0xB3,
                0x1A,
                0x78,
                0xF3,
                0x56,
                0x2B,
                0x1A,
                0xF6,
                0x72,
                0xE7,
                0xF3,
                0x90,
                0x7D,
                0x71,
                0x24,
                0x73,
                0x7F,
                0xDB,
                0x83,
                0x36,
                0x00,
                0x31,
                0x55,
                0x4E,
                0xB3,
                0x0D,
            ]
        )
        self.assertEqual(state_seeded[0:32], except_state)

        # Check if the counter is zero
        counter = bytearray(8)
        counter[7] = 64
        self.assertEqual(state_seeded[32:40], counter)

    def test_thash(self):
        # Initialize the state with a public seed
        pub_seed = bytes(i for i in range(16))
        seed_state(pub_seed)

        # Create a sample input and address
        input_data = bytes(16)  # Example input data, updated to zero-filled bytes
        inblocks = 1  # Number of input blocks
        addr = Address()
        # Expected output (this should be precomputed or obtained from a trusted source)
        expected_output = bytearray.fromhex(
            "8d23b2881d5e28ac54734379d5c3f681"
        )  # Updated to actual expected output

        # Output buffer
        output = bytearray(SPX_N)

        # Call the thash function
        thash(output, input_data, inblocks, pub_seed, addr)

        # Verify the output
        self.assertEqual(output, expected_output)

        # test case 7775da61232966d73d24493dd95020c3
        input_data = bytearray.fromhex("7775da61232966d73d24493dd95020c3")
        addr.set_chain_addr(3)
        expected_output = bytearray.fromhex("ec336f84ce7106c66a7974428a83db54")
        thash(output, input_data, inblocks, pub_seed, addr)
        self.assertEqual(output, expected_output)


if __name__ == "__main__":
    unittest.main()
