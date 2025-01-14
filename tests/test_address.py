import unittest
from spx.address import WOTSAddress, AddrType


class TestWOTSAddress(unittest.TestCase):
    def setUp(self):
        # 使用示例值设置一个 WOTSAddress 对象
        self.address = WOTSAddress()
        self.address.type = AddrType.WOTS_HASH
        self.address.key_pair = b"\x00\x00\x00\x03"
        self.address.chain = b"\x00\x00\x00\x04"
        self.address.hash = b"\x00\x00\x00\x05"

    def test_to_bytes(self):
        to_byte = self.address.to_bytes()
        except_byte = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00\x05"
        print(to_byte)
        self.assertEqual(to_byte, except_byte)


if __name__ == "__main__":
    unittest.main()
