# import unittest
# from spx.fors import fors_sign, fors_pk_from_sig, message_to_indices
# from spx.constant import (
#     SPX_FORS_BYTES,
#     SPX_FORS_PK_BYTES,
#     SPX_FORS_TREES,
#     SPX_FORS_HEIGHT,
#     SPX_N,
# )
# from spx.address import Address, AddrType
# import os


# class TestFORS(unittest.TestCase):
#     def setUp(self):
#         self.sk_seed = os.urandom(SPX_N)
#         self.pub_seed = os.urandom(SPX_N)
#         self.m = os.urandom((SPX_FORS_HEIGHT * SPX_FORS_TREES + 7) // 8)
#         self.fors_addr = Address()
#         self.sig = bytearray(SPX_FORS_BYTES)
#         self.pk = bytearray(SPX_FORS_PK_BYTES)
#         self.indices = bytearray(SPX_FORS_TREES)
#         message_to_indices(self.indices, self.m)

#     def test_fors_sign(self):
#         fors_sign(
#             self.sig, self.pk, self.m, self.sk_seed, self.pub_seed, self.fors_addr
#         )
#         # Verify that the signature is correctly generated
#         self.assertEqual(len(self.sig), SPX_FORS_BYTES)
#         self.assertEqual(len(self.pk), SPX_FORS_PK_BYTES)

#     def test_fors_pk_from_sig(self):
#         fors_sign(
#             self.sig, self.pk, self.m, self.sk_seed, self.pub_seed, self.fors_addr
#         )
#         derived_pk = bytearray(SPX_FORS_PK_BYTES)
#         fors_pk_from_sig(derived_pk, self.sig, self.m, self.pub_seed, self.fors_addr)
#         # Verify that the derived public key matches the original public key
#         self.assertEqual(derived_pk, self.pk)
