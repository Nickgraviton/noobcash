import time
from collections import OrderedDict
from Crypto.Hash import SHA256

class Block:
    """
    timestamp: Timestamp of block's creation
    index: Unique index of block
    list_of_transactions: List of transactions in this block
    previous_hash: Hash of previous block
    nonce: Nonce found through proof-of-work
    current_hash: Hash of current block
    """

    def __init__(self, index, list_of_transactions, previous_hash, nonce):
        self.timestamp = time.time()
        self.index = index
        self.list_of_transactions = list_of_transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.current_hash = hash()

    def to_dict(self):
        return OrderedDict({'timestamp': self.timestamp,
                            'index': self.index,
                            'list_of_transactions': self.list_of_transactions,
                            'previous_hash': self.previous_hash,
                            'nonce': self.nonce})

    def hash(self):
        return SHA256.new(json.dumps(self.to_dict()).encode('utf-8')).hexdigest()
