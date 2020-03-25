import time
import json
from Crypto.Hash import SHA256

from transaction import Transaction

class Block:
    """
    timestamp: Timestamp of block's creation
    index: Unique index of block
    list_of_transactions: List of transactions in this block
    previous_hash: Hash of previous block
    nonce: Nonce found through proof-of-work
    current_hash: Hash of current block
    """

    def __init__(self, index, list_of_transactions, previous_hash, nonce,
            timestamp=None, current_hash=None):
        self.index = index
        self.list_of_transactions = list_of_transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.timestamp = time.time() if timestamp is None else timestamp
        self.current_hash = self.hash() if current_hash is None else current_hash

    def to_dict_(self):
        sendable_transactions = [t.to_dict() for t in self.list_of_transactions]
        return {'timestamp': self.timestamp,
                'index': self.index,
                'list_of_transactions': sendable_transactions,
                'previous_hash': self.previous_hash,
                'nonce': self.nonce}

    # Sendable form of the object
    def to_dict(self):
        info = self.to_dict_()
        info['current_hash'] = self.current_hash
        return info

    # Restore Block after it's been sent to us with the to_dict function
    @staticmethod
    def from_dict(dictionary):
        list_of_transactions = [Transaction.from_dict(t) for t in dictionary['list_of_transactions']]
        dictionary['list_of_transactions'] = list_of_transactions

        return Block(**dictionary)

    def hash(self):
        h = SHA256.new(json.dumps(self.to_dict_(), sort_keys=True).encode('utf-8'))
        return h.hexdigest()
