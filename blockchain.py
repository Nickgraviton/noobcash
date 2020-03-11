class Blockchain:
    """
    DIFFICULTY: The number of 0s needed to find the proof of work
    CAPACITY: Number of transactions needed to form a block
    NODES: The number of nodes in the network
    blocks: The blocks in the blockchain
    transactions: Transactions not yet in a block
    nodes: A dictionary of the nodes in the network where the key is their public key
           and the value is a tuple of their IP, port and id
    utxos: A dictionary of the unspent transactions for each node in the network where
           the key is their public key and the value is tuples of the transaction ids
           and the corresponding amount
    """

    def __init__(self, difficulty, no_of_nodes):
        self.DIFFICULTY = difficulty
        self.CAPACITY = capacity
        self.NODES = no_of_nodes
        self.blocks = []
        self.transactions = []
        self.nodes = {}
        self.utxos = {}
