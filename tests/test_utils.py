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
    treehash,
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

    def test_treehash(self):
        # Initialize the state with a public seed
        pub_seed = bytes(i for i in range(16))
        seed_state(pub_seed)

        # Mock gen_leaf function
        def mock_gen_leaf(leaf, sk_seed, pub_seed, idx, tree_addr):
            return bytearray([idx] * SPX_N)

        # Create a sample address
        tree_addr = Address()
        tree_addr.set_type(1)

        # Prepare buffers for root and auth_path
        root = bytearray(SPX_N)
        auth_path = bytearray((2 * SPX_N))  # Assuming tree height of 8 for testing

        # Call the treehash function
        treehash(
            root, auth_path, bytes(SPX_N), pub_seed, 0, 0, 2, mock_gen_leaf, tree_addr
        )

        # Verify the root and auth_path (these values should be precomputed or obtained from a trusted source)
        all_leaf_values = bytearray(4 * SPX_N)
        for i in range(4):
            leaf = bytearray(SPX_N)
            leaf = mock_gen_leaf(leaf, bytes(SPX_N), pub_seed, i, tree_addr)
            all_leaf_values[i * SPX_N : (i + 1) * SPX_N] = leaf
        except_auth_path = bytearray(2 * SPX_N)
        # Assert the root
        tree_addr.set_tree_height(1)
        tree_addr.set_tree_index(0)
        except_auth_path[0:SPX_N] = all_leaf_values[SPX_N : SPX_N * 2]
        temp = bytearray(SPX_N)
        thash(
            temp,
            all_leaf_values[0 : 2 * SPX_N],
            2,
            pub_seed,
            tree_addr,
        )
        all_leaf_values[0:SPX_N] = temp
        tree_addr.set_tree_index(1)
        thash(
            temp,
            all_leaf_values[2 * SPX_N : 4 * SPX_N],
            2,
            pub_seed,
            tree_addr,
        )
        all_leaf_values[SPX_N : 2 * SPX_N] = temp
        except_auth_path[SPX_N : SPX_N * 2] = all_leaf_values[SPX_N : 2 * SPX_N]
        tree_addr.set_tree_height(2)
        tree_addr.set_tree_index(0)
        thash(
            temp,
            all_leaf_values[0 : 2 * SPX_N],
            2,
            pub_seed,
            tree_addr,
        )
        all_leaf_values[0:SPX_N] = temp
        expected_root = all_leaf_values[0:SPX_N]  # This is a placeholder value
        print(root.hex())
        self.assertEqual(root, expected_root)
        self.assertEqual(auth_path, except_auth_path)


if __name__ == "__main__":
    unittest.main()
