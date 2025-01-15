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
        seed_state(self.pub_seed)
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

    def test_wots_checksum(self):
        # Test wots_checksum function
        msg_base_w = bytearray([i for i in range(SPX_N)])
        msg_base_w = base_w(msg_base_w, SPX_WOTS_LEN1)

        csum_base_w = bytearray(SPX_WOTS_LEN2)
        expected_csum_base_w = bytearray(
            [1, 6, 8]
        )  # Expected output after computing checksum
        csum_base_w = wots_checksum(msg_base_w)
        self.assertEqual(csum_base_w, expected_csum_base_w)

    def test_wots_sign(self):
        """Test wots_sign function"""
        sig = bytearray(SPX_WOTS_LEN * SPX_N)
        wots_sign(sig, self.msg, self.sk_seed, self.pub_seed, self.addr)
        expected_sig = "d88a4c0779783e174e065c19727c6a70117b0857bf2beaadfa1d233a1765c6d3dbb54f3927a7970c7540f7391d935afeec336f84ce7106c66a7974428a83db54c532aa1faa0aefe95edbe51265114d61578990d7c086b3bffd4f98d669e0c4191a5ccc4a70d8a97b86277a6be5af329467e3dace6d1db34cd2d5ef30163f8060f5eea8a5fb026b31a8351df732310a7cc15df365af6e5cdcdb205b93c3cf3154a4aeadc896bf120a3223743763784f085ed532d9d33108c0aeda7329f9887e90fd8450761ecf14d38a232e0e9fcc27aa6338d03ca5e2ee72f68f24ee37f80ccd2adebe912703e6e7e3eff1426d69f1dc7f636c46e912c35b026fdbe72bfe85b5b87dc2848e80cbb8b4dbf32b354ede563c068dc9ea53399eee6ffb3a524b1def214029fb98efa77b7b0d53e5a4a56cc34be5c1b7a7699aff184947f25ab3a8acee9d8f9b9532bc20244c03a248f36dcd4f140bf632508ab4b4fe3472bdcc3f831fc4c154fd4c490f37254f20b7d347c65c9968f08ba4e01567cfa1ebd37df76c65aa55e3860def86d4ae4a1bf96a7db1d8ec0d70671846c1f754bd42fb421d3dae8871e822a6a123177a9f9b3f7e300259b13a34d63df002209d4724408961925186cfb7454d10f914af33722867e13c79e78d6ab4dad27d2ea0247866c115314ddb94cca150a81d56ba2359ca3a3ecf8a98c414007c141f45f1e85b012511be0af2822db8bb05a23aa78862bbce3c7d599841a7a45ab89673810c57e821db201a01a48f28535b7b8d6d873e89bc6902"  # Expected signature after computation
        self.assertEqual(sig.hex(), expected_sig)


if __name__ == "__main__":
    unittest.main()
