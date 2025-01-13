
from enum import Enum

class AddrType(Enum):
    WOTS = 0
    WOTSPK = 1
    HASHTREE = 2
    FORS_TREE = 3
    FORS_ROOTS = 4
    WOTS_KEY_GENERATE = 5
    FORS_KEY_GENERATE = 6

class Address:
    def __init__(self):
        self.layer = bytearray(4)    # 32-bit word
        self.tree = bytearray(12) 
        self.type = None

class WOTSAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.WOTS
        self.key_pair = bytearray(4)
        self.chain = bytearray(4)
        self.hash = bytearray(4)

class WOTSPKAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.WOTSPK
        self.key_pair = bytearray(4)

class HashTreeAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.HASHTREE
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
        
class WOTSKeyGenerateAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.WOTS_KEY_GENERATE
        self.key_pair = bytearray(4)
        self.chain = bytearray(4)
        self.hash = bytearray(4)
        
class FORSKeyGenerateAddress(Address):
    def __init__(self):
        super().__init__()
        self.type = AddrType.FORS_KEY_GENERATE
        self.key_pair = bytearray(4)
        self.tree_index = bytearray(4)
        self.tree_height = bytearray(4)
        
if __name__ == "__main__":
    addr = Address()
    print(addr.layer)
    print(addr.tree)
    print