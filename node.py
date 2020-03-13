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
        self.broadcast(data, "transaction")

    def broadcast_network_info(self):
        self.broadcast(self.network, "members")

    def broadcast_block(block):
        data = block.to_dict()
        self.broadcast(data, "block")

    def sign_transaction(self, transaction):
        key = RSA.importKey(self.wallet.private_key.encode())
        signer = PKCS1_v1_5.new(key)
        h = SHA256.new(json.dumps(transaction.transaction_id).encode('utf-8'))
        transaction.signature = binascii.hexlify(signer.sign(h)).encode('ascii')

    @staticmethod
    def validate_transaction(transaction):
        sender = transaction.sender_address
        key = RSA.importKey(sender.encode())
        verifier = PKCS1_v1_5.new(key)
        h = SHA256.new(json.dumps(transaction.transaction_id).encode('utf-8'))
        return verifier.verify(h,
                binascii.unhexlify(transaction.signature.decode('ascii')))


    def add_transaction(self, transaction_dict, blockchain):
        # Fetch transaction fields
        sender_address = transaction_dict['sender_address']
        recipient_address = transaction_dict['recipient_address']
        amount = transaction_dict['amount']
        timestamp = transaction_dict['timestamp']
        transaction_id = transaction_dict['transaction_id']
        signature = transaction_dict['signature']
        
        # Reconstruct transaction sent to us and validate it
        transaction = Transaction(sender_adress, recipient_address, amount, timestamp)
        transaction.signature = signature
        valid = validate_transaction(transaction)

        #get utxos and balance of sender, calculate if enough
        #add inputs and outputs to transaction
        transactions.append(transaction)

        if len(blockchain.transactions) == blockchain.CAPACITY:
            nonce = mine_block()
            block = Block()
            blockchain.blocks.append(block)
            broadcast_block(block)
            blockchain.transactions = []

    def mine_block():
        pass

    def valid_proof(block_dict, blockchain):
        # Fetch block fields
        timestamp = block_dict['timestamp']
        index = block_dict['index']
        list_of_transactions = block_dict['list_of_transactions']
        previous_hash = block_dict['previous_hash']
        nonce = block_dict['nonce']

        # Reconstruct block and check nonce
        block = Block(index, list_of_transactions, previous_hash, nonce, timestamp)

    def valid_chain(self, chain):
        #check for the longer chain accroose all nodes
        pass

    def resolve_conflicts(self):
        #resolve correct chain
        pass
