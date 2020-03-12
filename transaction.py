import time
import json
import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from collections import OrderedDict

import requests
from flask import Flask, jsonify, request, render_template

class Transaction_Input:
    """
    previous_output_id: Id of previous transaction output
    """

    def __init__(self, transaction_id):
        self.previous_output_id = transaction_id

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

    def to_dict(self):
        return self.transaction_dict['unique_id': self.unique_id]


class Transaction:
    """
    sender_address: Public key of sender's wallet
    recipient_address: Public key of recipient's wallet
    amount: Amount to be transferred
    timestamp: Timestamp of transaction
    transaction_id: Unique hash of transaction
    transaction_inputs: List of Transaction Input Objects
    transaction_outputs: List of Transaction Output Objects
    signature: Signature of transaction
    """

    def __init__(self, sender_address, recipient_address, amount):
        self.sender_address = sender_address
        self.recipient_address = recipient_address
        self.amount = amount
        self.timestamp = time.time()
        self.transaction_id = []
        self.transaction_inputs = []
        self.transaction_outputs = []
        self.signature = None

    def to_dict(self):
        transanction_inputs_to_dict = []

        for transaction_input in self.transaction_inputs:
            transanction_inputs_to_dict.append(transaction_input.to_dict())

        transanction_outputs_to_dict = []

        for transaction_output in self.transaction_outputs:
            transanction_outputs_to_dict.append(transaction_output.to_dict())

        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'amount': self.amount,
                            'timestamp': self.timestamp,
                            'transaction_id': self.transaction_id,
                            'transaction_inputs': transanction_inputs_to_dict,
                            'transaction_outputs': transanction_outputs_to_dict,
                            'signature': self.signature})

    def hash(self):
        return SHA256.new(json.dumps(self.to_dict()).encode('utf-8')).hexdigest()

##να δω με ποια λογικη κανει ετσι το hashing
##https://github.com/adilmoujahid/blockchain-python-tutorial/blob/master/blockchain_client/blockchain_client.py
##https://www.tutorialspoint.com/python_blockchain/python_blockchain_tutorial.pdf   σελίδα 12
