from enum import Enum

from spx.constant import *  # Import all constants from spx.constant


class AddrType(Enum):
    WOTS_HASH = 0
    WOTS_PK = 1
    TREE = 2
    FORS_TREE = 3
    FORS_ROOTS = 4
    WOTS_PRF = 5
    FORS_PRF = 6


class Address:
    def __init__(self):
        self._addr = bytearray(32)  # Ensure _addr is a bytearray
        self._type = None

    def set_layer_addr(self, layer: int) -> None:
        self._addr[SPX_OFFSET_LAYER] = layer

    def set_tree_addr(self, tree: int) -> None:
        self._addr[SPX_OFFSET_TREE : SPX_OFFSET_TREE + 8] = tree.to_bytes(8, "big")

    def set_type(self, type: int) -> None:
        self._addr[SPX_OFFSET_TYPE] = type

    def copy_subtree_addr(self, other: "Address") -> None:
        self._addr[: SPX_OFFSET_TREE + 8] = other._addr[: SPX_OFFSET_TREE + 8]

    def set_keypair_addr(self, keypair: int) -> None:
        if SPX_FULL_HEIGHT // SPX_D > 8:
            self._addr[SPX_OFFSET_KP_ADDR2] = keypair >> 8
        self._addr[SPX_OFFSET_KP_ADDR1] = keypair

    def copy_keypair_addr(self, other: "Address") -> None:
        self._addr[: SPX_OFFSET_TREE + 8] = other._addr[: SPX_OFFSET_TREE + 8]
        if SPX_FULL_HEIGHT // SPX_D > 8:
            self._addr[SPX_OFFSET_KP_ADDR2] = other._addr[SPX_OFFSET_KP_ADDR2]
        self._addr[SPX_OFFSET_KP_ADDR1] = other._addr[SPX_OFFSET_KP_ADDR1]

    def set_chain_addr(self, chain: int) -> None:
        self._addr[SPX_OFFSET_CHAIN_ADDR] = chain

    def set_hash_addr(self, hash: int) -> None:
        self._addr[SPX_OFFSET_HASH_ADDR] = hash

    def set_tree_height(self, tree_height: int) -> None:
        self._addr[SPX_OFFSET_TREE_HGT] = tree_height

    def set_tree_index(self, tree_index: int) -> None:
        self._addr[SPX_OFFSET_TREE_INDEX : SPX_OFFSET_TREE_INDEX + 4] = (
            tree_index.to_bytes(4, "big")
        )

    def to_bytes(self) -> bytes:
        return bytes(self._addr)
