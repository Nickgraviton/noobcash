from Crypto.PublicKey import RSA

class Wallet:
    """
    private key: The private key of the wallet used to sign transactions
    public key: The public key/address of the wallet
    """

    def __init__(self):
        key = RSA.generate(1024, Random.new().read)
        self.private_key = key.exportKey('PEM').decode('utf-8')
        self.public_key = key.publickey().exportKey('PEM').decode('utf-8')

    @staticmethod
    def balance(blockchain, public_key):
        transactions = blockchain.utxos[public_key]
        balance = 0
        for transaction in transactions:
            if transaction.recipient_address == public_key:
                balance += transaction.amount
        return balance
