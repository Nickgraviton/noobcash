import time
import json
from Crypto.Hash import SHA256
from collections import OrderedDict

class Transaction_Output:
    """
    origin_transaction_id: Id of transaction origin
    recipient address: Address of transaction's recipient
    amount: Amount to be transferred with this transaction
    transactions_dict: Dictionary of transaction details along with unique timestamp
    unique_id: Unique id created based on the transaction's details
    """

    def __init__(self, origin_transaction_id, recipient_address, amount, unique_id=None):
        self.origin_transaction_id = origin_transaction_id
        self.recipient_address = recipient_address
        self.amount = amount
        self.unique_id = self.hash() if unique_id is None else unique_id

    # Helper function used in hash and to_dict
    def to_dict_(self):
        return OrderedDict({'origin_transaction_id': self.origin_transaction_id,
                            'recipient_address': self.recipient_address,
                            'amount': self.amount})

    # Sendable form of the object
    def to_dict(self):
        info = self.to_dict_()
        info['unique_id'] = self.unique_id
        return info

    # Restore Transaction_Output after it's been sent to us with the to_dict function
    @staticmethod
    def from_dict(dictionary):
        return Transaction_Output(**dictionary)

    # Use the helper dictionary and a timestamp to make a unique id
    def hash(self):
        info = self.to_dict_()
        info['timestamp'] = time.time()
        return SHA256.new(json.dumps(info).encode('utf-8')).hexdigest()


class Transaction:
    """
    sender_address: Public key of sender's wallet
    recipient_address: Public key of recipient's wallet
    amount: Amount to be transferred
    timestamp: Timestamp of transaction. If provided we use the given value
               else we get the current timestamp
    id: Unique hash of transaction
    inputs: List of transaction input ids
    outputs: List of Transaction Output Objects
    signature: Signature of transaction
    """

    def __init__(self, sender_address, recipient_address, amount,
            timestamp=None, id_=None, signature=None):

        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.amount = amount
        self.timestamp = time.time() if timestamp is None else timestamp
        self.id = self.hash() if id_ is None else id_
        self.signature = signature
        self.inputs = []
        self.outputs = []

    # Function used to create a dictionary to sign the transaction
    def to_dict_(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'amount': self.amount,
                            'timestamp': self.timestamp})

    # Function used to create a dictionary of a transaction to be sent
    def to_dict(self):
        info = self.to_dict_()
        info['id_'] = self.id
        info['signature'] = self.signature
        return info

    # Restore Transaction after it's been sent to us with the to_dict function
    @staticmethod
    def from_dict(dictionary):
        return Transaction(**dictionary)

    def hash(self):
        return SHA256.new(json.dumps(self.to_dict_()).encode('utf-8')).hexdigest()
