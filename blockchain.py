from collections import OrderedDict

class Blockchain:
    """
    DIFFICULTY: The number of 0s needed to find the proof of work
    CAPACITY: Number of transactions needed to form a block
    blocks: The blocks in the blockchain
    transactions: Transactions not yet in a block
    utxos: A dictionary of the unspent transactions for each node in the
           network where the key is their public key and the value is a
           list of transaction output object
    """

    def __init__(self, difficulty = 4, capacity = 5):
        self.DIFFICULTY = difficulty
        self.CAPACITY = capacity
        self.blocks = []
        self.transactions = []
        self.utxos = {}

    def to_dict(self):
        return OrderedDict({'blocks': self.blocks,
                            'transactions': self.transactions,
                            'utxos': self.utxos})
