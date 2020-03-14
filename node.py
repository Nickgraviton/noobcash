from random import seed
from random import randint
import requests
import block
import transaction
import wallet

class Node:
    """
    id: Id of node
    no_of_nodes: number of nodes in the network
    network: Dictionary of the network's participant where the key
             is the puplic key and the value is a dictionary
             with the ip, port and id of each participant
    wallet: Wallet containing the public and private key
    """

    def __init__(self):
        self.id = 0
        self.no_of_nodes = None
        self.network = {}
        self.wallet = Wallet()

    def register_node_to_network(self, public_key, member_ip, port):
        next_id = len(network)
        self.network[public_key: {'ip': member_ip,
                                  'port': port,
                                  'id': next_id}]
        return next_id

    def broadcast(self, data, endpoint):
        for n, info in self.network:
            ip = info['ip']
            port = info['port']
        requests.post(f'{ip}:{port}/{endpoint}', data)
    
    def broadcast_transaction(self, sender, receiver, amount):
        transaction = Transaction(sender, receiver, amount)
        self.sign_transaction(transaction)
        data = transaction.to_dict()
        self.broadcast(data, 'transaction')

    def broadcast_network_info(self):
        self.broadcast(self.network, 'members')

    def broadcast_block(block):
        data = block.to_dict()
        data['current_hash'] = block.current_hash
        self.broadcast(data, 'block')

    def sign_transaction(self, transaction):
        key = RSA.importKey(self.wallet.private_key.encode())
        signer = PKCS1_v1_5.new(key)
        h = SHA256.new(json.dumps(transaction.id).encode('utf-8'))
        transaction.signature = binascii.hexlify(signer.sign(h)).encode('ascii')

    @staticmethod
    def validate_transaction(transaction):
        sender = transaction.sender_address
        key = RSA.importKey(sender.encode())
        verifier = PKCS1_v1_5.new(key)
        h = SHA256.new(json.dumps(transaction.id).encode('utf-8'))
        return verifier.verify(h,
                binascii.unhexlify(transaction.signature.decode('ascii')))


    def add_transaction(self, transaction_dict, blockchain):
        # Fetch transaction fields
        sender_address = transaction_dict['sender_address']
        recipient_address = transaction_dict['recipient_address']
        amount = transaction_dict['amount']
        timestamp = transaction_dict['timestamp']
        transaction_id = transaction_dict['id']
        signature = transaction_dict['signature']
        
        # Reconstruct transaction sent to us and validate it
        transaction = Transaction(sender_adress, recipient_address, amount, timestamp)
        transaction.signature = signature
        valid = validate_transaction(transaction)

        if not valid:
            return False
        else:
            balance = Wallet.balance(blockchain, sender_address)
            if balance < amount:
                return False

            temp_sum = 0
            inputs = []
            utxos_to_be_removed = []

            for utxo in utxos[sender_address]:
                utxos_to_be_removed.append(utxo)
                transaction.inputs.append(
                        Transaction_Input(utxo.origin_transaction_id))
                temp_sum += utxo.amount
                if temp_sum >= amount:
                    break

            for utxo in utxos_to_be_removed:
                utxos[sender_address].remove(utxo)

            # Add output to transaction and update utxos
            transaction_result = Transaction_Output(transaction_id,
                recipient_address, amount)
            transaction.outputs.append(transaction_result)
            utxos[recipient_address].append(transaction_result)

            # Check if we need to give change back to the sender
            if temp_sum > amount:
                change = Transaction_Output(transaction_id,
                    sender_address, temp_sum - amount)
                transaction.outputs.append(change)
                utxos[recipient_address].append(change)

            blockchain.transactions.append(transaction)

            if len(blockchain.transactions) == blockchain.CAPACITY:
                nonce = self.mine_block(blockchain)


    def mine_block():
        seed(1)
        nonce = randint(0, 4294967295)
        block = Block(blockchain.blocks[-1].index + 1, blockchain.transactions,
                blockchain.blocks[-1].current_hash, nonce)
        while True:
            block.nonce = nonce
            block.current_hash = block.hash()
            if block.current_hash.startswith('0' * blockchain.DIFFICULTY):
                broadcast_block(block)
                break
            nonce += 1

        blockchain.blocks.append(block)
        blockchain.transactions = []

    def valid_proof(block_dict, blockchain):
        # Fetch block fields
        timestamp = block_dict['timestamp']
        index = block_dict['index']
        list_of_transactions = block_dict['list_of_transactions']
        previous_hash = block_dict['previous_hash']
        nonce = block_dict['nonce']
        current_hash = block_dict['current_hash']

        # Reconstruct block
        block = Block(index, list_of_transactions, previous_hash, nonce, timestamp)
        if len(list_of_transactions) != blockchain.DIFFICULTY:
            return False
        # When we instantiate an object, the current hash is calculated so we compare
        # it to the one the was sent to us
        if not current_hash == block.current_hash:
            return False
        if not block.current_hash.startswith('0' * blockchain.DIFFICULTY):
            return False
        if blockchain.blocks[-1].current_hash != previous_hash:
            # Invalid previous hash
            # The chain could be longer somewhere so we need to ask

        # All previous checks succeeded


    def valid_chain(self, chain):
        #check for the longer chain accroose all nodes
        pass

    def resolve_conflicts(self):
        #resolve correct chain
        pass
