from enum import Enum


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
        self.layer = bytearray(4)  # 32-bit word
        self.tree = bytearray(12)
        self.type = None


class WOTSAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.WOTS_HASH
        self.key_pair = bytearray(4)
        self.chain = bytearray(4)
        self.hash = bytearray(4)

    def to_bytes(self):
        type = self.type.value.to_bytes(4, "big")
        return self.layer + self.tree + type + self.key_pair + self.chain + self.hash


class WOTSPKAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.WOTS_PK
        self.key_pair = bytearray(4)


class TreeAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.TREE
        self.tree_index = bytearray(4)
        self.tree_height = bytearray(4)


class FORSTreeAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.FORS_TREE
        self.key_pair = bytearray(4)
        self.tree_index = bytearray(4)
        self.tree_height = bytearray(4)


class FORSRootsAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.FORS_ROOTS
        self.key_pair = bytearray(4)


class WOTSPrfAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.WOTS_PRF
        self.key_pair = bytearray(4)
        self.chain = bytearray(4)
        self.hash = bytearray(4)


class FORSPrfAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.FORS_PRF
        self.key_pair = bytearray(4)
        self.tree_index = bytearray(4)
        self.tree_height = bytearray(4)


if __name__ == "__main__":
    addr = Address()
    print(addr.layer)
    print(addr.tree)
    print
