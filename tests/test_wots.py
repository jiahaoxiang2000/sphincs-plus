import unittest
from spx.utils import seed_state
from spx.wots import *
from spx.address import Address
import os


class TestWOTS(unittest.TestCase):
    def setUp(self):
        # Setup common test values
        self.sk_seed = bytearray(i for i in range(SPX_N))
        self.pub_seed = bytearray(i for i in range(SPX_N))
        self.addr = Address()
        self.msg = bytearray(i for i in range(SPX_N))  # Random test message

    def test_wots_gen_pk(self):
        seed_state(self.pub_seed)
        pk = wots_gen_pk(self.sk_seed, self.pub_seed, self.addr)
        except_pk = "66281ffd64473d5e835e8b9ac68e25a41c91ddc55f1f83163cc66d6697ab680b5be52ff5fcf4965aeb39a4297f3b6e8ae8f025a2dd8d2ebfd659751cd85ec17a712424016fbcd7e07abff59b1a9039b3fc48b123cd3754194fd674a060c060dc57ea11c83549ff77261a8aaa5d03138b67463d71b13933628ba3bfd35b1b5cc8678ce611794546103bf29dce7aa708b8b78b336d5a1053ea5392d5b6a63ae268ce3f680304b75e9e1f4c1f180268f71ecf20fb257aeb8d048bac76e154d9051c31e441e7b47d6b355bd23f0efdd384e205773860df399b80cfbb06bc31000593509235335eadba10348c2aa73341ed03652cb8fd9615c57b5ddcf29c01070be586a5ccdb995d313caa131f796c853bdcc53beec51b6f6b0f6c9ff066b769f356bae9140486d3a9ef3e1a3296bac21133e3f89e96726a8f6d80d8810fd37ea7e8896d2eb7ea4eb254f53c971e45e0fe454a6ae1649f452ae1bdc35f25556f6a1e5e94fe3893b806d0b9872ddc7625045ed9e53ee9e16ce4a394ec04529892e8f11d92166ef4a83ed460121b3f86146921962c60a225f0aa3cab3b0b7e86167400ce9b02e9219d89c1f87ee541c639d2f4fa2159e8e59e99f77a0a4b3790d2c4af4d3ed7e014b4b8a47f141bf47b77d93f4e069bcdcdda9a334cfe30ce53dbfcb826e1d252eb878da59176a10b3e609ff08a98c414007c141f45f1e85b012511be03a7525c3c311011679311cc2e663f32ccec8630d1cf1fee8dd1fb693c952b3c397375b8a2a4709f189062c40e16c7b1"
        self.assertEqual(pk.hex(), except_pk)

    def test_base_w(self):
        # Test base_w function
        msg = bytearray([0b11110000, 0b10101010])
        out_len = 4
        expected_output = bytearray(
            [0b1111, 0b0000, 0b1010, 0b1010]
        )  # Base-w conversion of the input
        self.assertEqual(base_w(msg, out_len), expected_output)


if __name__ == "__main__":
    unittest.main()
