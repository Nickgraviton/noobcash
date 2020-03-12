import block
import wallet

class Node:
    """
    id: Id of node
    network: Dictionary of the network's participant where the key
             is the puplic key and the value is a dictionary
             with the ip, port and id of each participant
    wallet: Wallet containg the public and private key
    """

    def __init__():
        self.id = 0
        self.network = {}
        self.wallet = Wallet()

    def register_node_to_network(self, public_key, member_ip, port):
        next_id = len(network)
        self.network[public_key: {'ip': member_ip,
                                  'port': port,
                                  'id': next_id}]
        return

    def broadcast_transaction(sender, receiver, amount):
        transaction = Transaction(sender, receiver, signature)
        transaction.signature = sign_transaction(transaction)
        for n, info in network:
            ip = info['ip']
            port = info['port']
        requests.post(f'{ip}:{port}/transaction', transaction.to_dict())
        return

    def validate_transaction(transaction):
        sender = transaction.sender_address
        key = RSA.importKey(sender.encode())
        verifier = PKCS1_v1_5.new(key)
        info = OrderedDict({'sender_address': transaction.sender_address,
                            'recipient_address': transaction.recipient_address,
                            'amount': transaction.amount,
                            'timestamp': transaction.timestamp})
        
        h = SHA256.new(json.dumps(info).encode('utf-8'))
        return verifier.verify(h,
                binascii.unhexlify(transaction.signature.decode('ascii')))

    def sign_transaction(self, transaction):
        key = RSA.importKey(self.wallet.private_key.encode())
        signer = PKCS1_v1_5.new(key)
        info = OrderedDict({'sender_address': transaction.sender_address,
                            'recipient_address': transaction.recipient_address,
                            'amount': transaction.amount,
                            'timestamp': transaction.timestamp})

        h = SHA256.new(json.dumps(info).encode('utf-8'))
        return binascii.hexlify(signer.sign(h)).encode('ascii')


    def add_transaction_to_block():
        #if enough transactions  mine

    def mine_block():

    def broadcast_block():

    def valid_proof(.., difficulty=MINING_DIFFICULTY):
        #concencus functions

    def valid_chain(self, chain):
        #check for the longer chain accroose all nodes

    def resolve_conflicts(self):
        #resolve correct chain
