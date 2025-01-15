import unittest
from spx.address import Address, AddrType
from spx.constant import *  # Import all constants from spx.constant


class TestAddress(unittest.TestCase):
    def setUp(self):
        self.address = Address()

    def test_set_layer_addr(self):
        self.address.set_layer_addr(5)
        self.assertEqual(self.address._addr[SPX_OFFSET_LAYER], 5)

    def test_set_tree_addr(self):
        self.address.set_tree_addr(123456789)
        self.assertEqual(
            int.from_bytes(
                self.address._addr[SPX_OFFSET_TREE : SPX_OFFSET_TREE + 8], "big"
            ),
            123456789,
        )

    def test_set_type(self):
        self.address.set_type(AddrType.WOTS_HASH.value)
        self.assertEqual(self.address._addr[SPX_OFFSET_TYPE], AddrType.WOTS_HASH.value)

    def test_copy_subtree_addr(self):
        other_address = Address()
        other_address.set_tree_addr(987654321)
        self.address.copy_subtree_addr(other_address)
        self.assertEqual(
            int.from_bytes(
                self.address._addr[SPX_OFFSET_TREE : SPX_OFFSET_TREE + 8], "big"
            ),
            987654321,
        )

    def test_set_keypair_addr(self):
        self.address.set_keypair_addr(123)
        self.assertEqual(self.address._addr[SPX_OFFSET_KP_ADDR1], 123)
        # Assuming SPX_FULL_HEIGHT // SPX_D <= 8, so no need to check SPX_OFFSET_KP_ADDR2

    def test_copy_keypair_addr(self):
        other_address = Address()
        other_address.set_keypair_addr(200)
        self.address.copy_keypair_addr(other_address)
        self.assertEqual(self.address._addr[SPX_OFFSET_KP_ADDR1], 200)
        # Assuming SPX_FULL_HEIGHT // SPX_D <= 8, so no need to check SPX_OFFSET_KP_ADDR2

    def test_set_chain_addr(self):
        self.address.set_chain_addr(210)
        self.assertEqual(self.address._addr[SPX_OFFSET_CHAIN_ADDR], 210)

    def test_set_hash_addr(self):
        self.address.set_hash_addr(101)
        self.assertEqual(self.address._addr[SPX_OFFSET_HASH_ADDR], 101)

    def test_set_tree_height(self):
        self.address.set_tree_height(2)
        self.assertEqual(self.address._addr[SPX_OFFSET_TREE_HGT], 2)

    def test_set_tree_index(self):
        self.address.set_tree_index(300)
        self.assertEqual(
            int.from_bytes(
                self.address._addr[SPX_OFFSET_TREE_INDEX : SPX_OFFSET_TREE_INDEX + 4],
                "big",
            ),
            300,
        )

    def test_to_bytes(self):
        self.address.set_layer_addr(5)
        self.address.set_tree_addr(123456789)
        self.address.set_type(AddrType.WOTS_HASH.value)
        self.address.set_keypair_addr(123)
        self.address.set_chain_addr(200)
        self.address.set_hash_addr(101)
        self.address.set_tree_height(2)
        self.address.set_tree_index(300)

        expected_bytes = bytearray(32)
        expected_bytes[SPX_OFFSET_LAYER] = 5
        expected_bytes[SPX_OFFSET_TREE : SPX_OFFSET_TREE + 8] = int.to_bytes(
            123456789, 8, "big"
        )
        expected_bytes[SPX_OFFSET_TYPE] = AddrType.WOTS_HASH.value
        expected_bytes[SPX_OFFSET_KP_ADDR1] = 123
        expected_bytes[SPX_OFFSET_CHAIN_ADDR] = 200
        expected_bytes[SPX_OFFSET_HASH_ADDR] = 101
        expected_bytes[SPX_OFFSET_TREE_HGT] = 2
        expected_bytes[SPX_OFFSET_TREE_INDEX : SPX_OFFSET_TREE_INDEX + 4] = (
            int.to_bytes(300, 4, "big")
        )

        self.assertEqual(self.address.to_bytes(), bytes(expected_bytes))


if __name__ == "__main__":
    unittest.main()
