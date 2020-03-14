import time
import json
from Crypto.Hash import SHA256
from collections import OrderedDict

class Transaction_Input:
    """
    previous_output_id: Id of previous transaction output
    """

    def __init__(self, previous_output_id):
        self.previous_output_id = previous_output_id

    def to_dict(self):
        return OrderedDict({'previous_output_id': self.previous_output_id})


class Transaction_Output:
    """
    origin_transaction_id: Id of transaction origin
    recipient address: Address of transaction's recipient
    amount: Amount to be transferred with this transaction
    transactions_dict: Dictionary of transaction details along with unique timestamp
    unique_id: Unique id created based on the transaction's details
    """

    def __init__(self, origin_transaction_id, recipient_address, amount):
        self.origin_transaction_id = origin_transaction_id
        self.recipient_address = recipient_address
        self.amount = amount
        self.transaction_dict = OrderedDict({'origin_transaction_id': origin_transaction_id,
                                             'recipient_address': recipient_address,
                                             'amount': amount,
                                             'timestamp': time.time()})
        self.unique_id = SHA256.new(json.dumps(transaction_dict).encode('utf-8')).hexdigest()
        self.transaction_dict['unique_id'] = self.unique_id
    
    def to_dict(self):
        return self.transaction_dict


class Transaction:
    """
    sender_address: Public key of sender's wallet
    recipient_address: Public key of recipient's wallet
    amount: Amount to be transferred
    timestamp: Timestamp of transaction. If provided we used the given value
               else we get the current timestamp
    id: Unique hash of transaction
    inputs: List of Transaction Input Objects
    outputs: List of Transaction Output Objects
    signature: Signature of transaction
    """

    def __init__(self, sender_address, recipient_address, amount, timestamp=None):
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.amount = amount
        if timestamp == None:
            self.timestamp = time.time()
        else:
            self.timestamp = timestamp
        self.id = self.hash()
        self.inputs = []
        self.outputs = []
        self.signature = None

    # Function used to create a dictionary to sign the transaction
    def _to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'amount': self.amount,
                            'timestamp': self.timestamp})

    # Function used to create a dictionary of a transaction to be sent
    def to_dict(self):
        info = self._to_dict()
        info['id'] = self.id
        info['signature'] = self.signature
        return info

    def hash(self):
        return SHA256.new(json.dumps(self._to_dict()).encode('utf-8')).hexdigest()
