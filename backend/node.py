from Crypto.Random import random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import requests
import json
import base64
import copy
import threading
import time

from block import Block
from blockchain import Blockchain
from properties import DIFFICULTY, CAPACITY
from transaction import Transaction, Transaction_Output
from wallet import Wallet

class Node:
    """
    id_: Id of node
    no_of_nodes: number of nodes in the network
    network: Dictionary of the network's participant where the key
             is the puplic key and the value is a dictionary
             with the ip, port and id of each participant
    wallet: Wallet containing the public and private key
    miner: The thread running the miner so that mining doesn't
           block the application
    mine_event: Event we set to signal to the miner that he can mine
    mine_time: Sum of the mine time of all blocks
    mine_counter: Times we successfully mined a block
    """

    def __init__(self):
        self.id_ = 0
        self.no_of_nodes = None
        self.network = {}
        self.wallet = Wallet()
        self.miner = None
        self.mine_event = threading.Event()
        self.mine_time = 0
        self.mine_counter = 0

    def register_node_to_network(self, public_key, member_ip, port):
        next_id = len(self.network)
        self.network[public_key] = {'ip': member_ip,
                                    'port': port,
                                    'id_': next_id}
        return next_id

    def broadcast(self, data, endpoint):
        for n, info in self.network.items():
            if n != self.wallet.public_key:
                ip = info['ip']
                port = info['port']
                requests.post('http://{}:{}/{}'.format(ip, port, endpoint), json=data)
    
    def broadcast_transaction(self, transaction):
        data = transaction.to_dict()
        self.broadcast(data, 'transaction/remote')

    def broadcast_network_info(self):
        self.broadcast(self.network, 'members')

    def broadcast_block(self, block):
        data = block.to_dict()
        self.broadcast(data, 'block')

    def sign_transaction(self, transaction):
        key = RSA.import_key(self.wallet.private_key.encode())
        signer = pkcs1_15.new(key)

        h = SHA256.new(json.dumps(transaction.to_dict_(), sort_keys=True).encode('utf-8'))
        # Encode in base64 so that it is compatible with the format json expects
        transaction.signature = base64.b64encode(signer.sign(h)).decode('utf-8')

    @staticmethod
    def validate_transaction(transaction):
        sender = transaction.sender_address
        key = RSA.import_key(sender.encode())
        verifier = pkcs1_15.new(key)

        h = SHA256.new(json.dumps(transaction.to_dict_(), sort_keys=True).encode('utf-8'))
        # Verify function raises ValueError if signature is not valid
        try:
            verifier.verify(h, base64.b64decode(transaction.signature))
            return True
        except ValueError:
            return False

    # Function to create and broadcast new transaction
    def create_transaction(self, recipient_address, amount, blockchain):
        if recipient_address == self.wallet.public_key or amount <= 0:
            return False

        transaction = Transaction(self.wallet.public_key, recipient_address, amount)
        self.sign_transaction(transaction)

        balance = Wallet.balance(blockchain, transaction.sender_address)
        if balance < transaction.amount:
            return False

        temp_sum = 0
        transaction.inputs = []
        utxos_to_be_removed = []
        
        # Find which inputs need to be used for the transaction
        for utxo in blockchain.utxos[transaction.sender_address]:
            utxos_to_be_removed.append(utxo)
            transaction.inputs.append(utxo.origin_transaction_id)
            temp_sum += utxo.amount
            if temp_sum >= transaction.amount:
                break

        with blockchain.lock:
            for utxo in utxos_to_be_removed:
                blockchain.utxos[transaction.sender_address].remove(utxo)

            # Add output to transaction and update utxos
            transaction_result = Transaction_Output(transaction.id_,
                transaction.recipient_address, transaction.amount)
            transaction.outputs.append(transaction_result)

            if transaction.recipient_address in blockchain.utxos:
                blockchain.utxos[transaction.recipient_address].append(transaction_result)
            else:
                blockchain.utxos[transaction.recipient_address] = []
                blockchain.utxos[transaction.recipient_address].append(transaction_result)

            # Check if we need to give change back to the sender
            if temp_sum > transaction.amount:
                change = Transaction_Output(transaction.id_,
                    transaction.sender_address, temp_sum - transaction.amount)
                transaction.outputs.append(change)
                blockchain.utxos[transaction.sender_address].append(change)
            
            blockchain.transactions.append(transaction)

        self.broadcast_transaction(transaction)

        if len(blockchain.transactions) >= CAPACITY:
            self.mine_event.set()

        return True

    # Function to check transaction sent to us
    def add_transaction(self, transaction_dict, blockchain, part_of_block=False):
        # Reconstruct transaction sent to us and validate it
        transaction  = Transaction.from_dict(transaction_dict)
        valid = self.validate_transaction(transaction)

        if not valid:
            return False

        temp_sum = 0
        utxos_to_be_removed = []

        # We check if all the transaction inputs sent to us are correct
        for transaction_input in transaction.inputs:
            correct_input = False
            for utxo in blockchain.utxos[transaction.sender_address]:
                if transaction_input == utxo.origin_transaction_id:
                    correct_input = True
                    utxos_to_be_removed.append(utxo)
                    temp_sum += utxo.amount

            # Transaction input was not found in the utxo list
            if not correct_input:
                return False

        # Give transaction inputs are not enough
        if temp_sum < transaction.amount:
            return False

        with blockchain.lock:
            for utxo in utxos_to_be_removed:
                blockchain.utxos[transaction.sender_address].remove(utxo)

            # Add output to transaction and update utxos
            transaction_result = Transaction_Output(transaction.id_,
                transaction.recipient_address, transaction.amount)
            transaction.outputs.append(transaction_result)

            # If utxo list of wallet is empty initialize it to an empty list
            if transaction.recipient_address in blockchain.utxos:
                blockchain.utxos[transaction.recipient_address].append(transaction_result)
            else:
                blockchain.utxos[transaction.recipient_address] = []
                blockchain.utxos[transaction.recipient_address].append(transaction_result)

            # Check if we need to give change back to the sender
            if temp_sum > transaction.amount:
                change = Transaction_Output(transaction.id_,
                    transaction.sender_address, temp_sum - transaction.amount)
                transaction.outputs.append(change)
                blockchain.utxos[transaction.sender_address].append(change)

            # If the transaction was part of a block we don't add it as a pending transaction
            if not part_of_block:
                blockchain.transactions.append(transaction)

        # This part is unlocked because the miner needs the lock
        if len(blockchain.transactions) >= CAPACITY:
            self.mine_event.set()

        return True

    def mine_block(self, blockchain):
        while True:
            self.mine_event.wait()

            # Remove pending transactions that we received in a block
            with blockchain.lock:
                to_be_removed = []
                for transaction in blockchain.transactions:
                    if transaction.id_ in blockchain.transactions_set:
                        to_be_removed.append(transaction)
                for transaction in to_be_removed:
                    blockchain.transactions.remove(transaction)

            if len(blockchain.transactions) < CAPACITY:
                self.mine_event.clear()
                continue                   

            with blockchain.lock:
                # Copy CAPACITY transactions that will be put inside of block
                transactions = copy.deepcopy(blockchain.transactions[:CAPACITY])

            start = time.time()

            nonce = random.randint(0, 4294967295)
            block = Block(blockchain.blocks[-1].index + 1, transactions,
                    blockchain.blocks[-1].current_hash, nonce)
            while True:
                block.nonce = nonce
                block.current_hash = block.hash()
                if block.current_hash.startswith('0' * DIFFICULTY):
                    break
                nonce = (nonce + 1) % 4294967295

            end = time.time()
            self.mine_time += end - start
            self.mine_counter += 1

            # Acquire the lock inside the if statement because valid proof also uses the lock
            status = self.valid_proof(block, blockchain)
            if status == 'success':
                with blockchain.lock:
                    for transaction in block.list_of_transactions:
                        # Our block has a transaction that is already in the blockchain
                        if transaction.id_ in blockchain.transactions_set:
                            continue
                    for transaction in block.list_of_transactions:
                        blockchain.transactions_set.add(transaction.id_)
                    blockchain.blocks.append(block)
                self.broadcast_block(block)

    def valid_proof(self, block, blockchain, previous_hash=None):
        # Invalid number of transactions in block
        if len(block.list_of_transactions) != CAPACITY:
            return 'block does not have capacity transactions'

        # Check if valid hash
        if  block.hash() != block.current_hash:
            return 'hashes do not match'

        # Invalid nonce
        if not block.current_hash.startswith('0' * DIFFICULTY):
            return 'invalid nonce'

        # New block was found so we check if it can be added to the end of our blockchain
        if previous_hash is None:
            # Invalid previous hash for the chain's end
            if blockchain.blocks[-1].current_hash != block.previous_hash:
                # The new block may have a previous hash equal to the hash of  a block already
                # in the blockchain. In that case we drop it since it leads to a smaller chain
                for b in blockchain.blocks[:-1]:
                    if b.current_hash == block.previous_hash:
                        return 'dropped block since it leads to smaller chain'
                # Otherwise the chain could be longer somewhere so we need to ask
                self.resolve_conflicts(blockchain)
                return 'resolved conflict'
        # We check if an existing block's previous hash is equal to the the previous block's hash
        else:
            if previous_hash != block.previous_hash:
                return 'hashes do not match'

        # All previous checks succeeded
        return 'success'

    def valid_chain(self, blockchain):
        # Validate all blocks except for the first one
        for i, b in enumerate(blockchain.blocks[:-1]):
            # Send the current block along with the hash of its previous block
            status = self.valid_proof(blockchain.blocks[i+1], blockchain,
                    blockchain.blocks[i].current_hash)
            if status != 'success':
                return False 
        return True

    # Consensus algorithm
    def resolve_conflicts(self, blockchain):
        responses = []
        for n, info in self.network.items():
            if n != self.wallet.public_key:
                ip = info['ip']
                port = info['port']
                response = requests.get('http://{}:{}/blockchain'.format(ip, port))
                responses.append(response)

        max_chain_length = len(blockchain.blocks)
        with blockchain.lock:
            for response in responses:
                blockchain_dict = response.json()
                peer_blockchain = Blockchain.from_dict(blockchain_dict)

                # Keep the longest chain
                if len(peer_blockchain.blocks) > max_chain_length:
                    max_chain_length = len(peer_blockchain.blocks)
                    blockchain.blocks = peer_blockchain.blocks
                    blockchain.transactions = peer_blockchain.transactions
                    blockchain.utxos = peer_blockchain.utxos
