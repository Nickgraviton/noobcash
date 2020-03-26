import threading

from block import Block
from transaction import Transaction, Transaction_Output

class Blockchain:
    """
    blocks: The blocks in the blockchain
    transactions: Transactions not yet in a block
    utxos: A dictionary of the unspent transactions for each node in the
           network where the key is their public key and the value is a
           list of transaction output objects
    transactions_set: A set of unique transaction ids to avoid double spending
    lock: Blockchain lock to ensure mutual exclusion between the flask and the miner threads
    """

    def __init__(self, blocks=[], transactions=[], utxos={}):
        self.blocks = blocks
        self.transactions = transactions
        self.utxos = utxos
        self.transactions_set = set()
        self.lock = threading.Lock()

    # Sendable form of the object
    def to_dict(self):
        sendable_blocks = [b.to_dict() for b in self.blocks]
        sendable_transactions = [t.to_dict() for t in self.transactions]
        sendable_utxos = {}
        for key, values in self.utxos.items():
            sendable_utxos[key] = [v.to_dict() for v in values]

        return {'blocks': sendable_blocks,
                'transactions': sendable_transactions,
                'utxos': sendable_utxos}

    # Restore Blockchain after it's been sent to us with the to_dict function
    @staticmethod
    def from_dict(dictionary):
        blocks = [Block.from_dict(b) for b in dictionary['blocks']]
        dictionary['blocks'] = blocks

        transactions = [Transaction.from_dict(t) for t in dictionary['transactions']]
        dictionary['transactions'] = transactions

        utxos = {}
        for key, values in dictionary['utxos'].items():
            utxos[key] = [Transaction_Output.from_dict(txo) for txo in values]
        dictionary['utxos'] = utxos

        return Blockchain(**dictionary)
