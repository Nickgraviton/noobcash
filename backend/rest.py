import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from properties import COORDINATOR_IP, COORDINATOR_PORT
from block import Block
from node import Node
from blockchain import Blockchain
from transaction import Transaction, Transaction_Output

app = Flask(__name__)
CORS(app)

FLASK_PORT = None
# Create the blockchain and initialize the node
blockchain = Blockchain()
node = Node()

#--------------------------------------------------------------------
#------------------------------REST API------------------------------
#--------------------------------------------------------------------

# Endpoint where other members can request our blockchain
@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    return jsonify(blockchain.to_dict()), 200

# Endpoint where other members can send us their blockchain
@app.route('/blockchain', methods=['POST'])
def post_blockchain():
    blockchain_dict = request.get_json()
    peer_blockchain = Blockchain.from_dict(blockchain_dict)

    # Empty blockchain in our node so far which means the coordinator
    # sent us the current blockchain
    if not blockchain.blocks:
        valid = node.valid_chain(peer_blockchain)
        if not valid:
            return jsonify('invalid block'), 400
        blockchain.blocks = peer_blockchain.blocks
        blockchain.transactions = peer_blockchain.transactions
        blockchain.utxos = peer_blockchain.utxos
    return jsonify(''), 200

# Endpoint where other members send us transactions
@app.route('/transaction', methods=['POST'])
def post_transaction():
    transaction_dict = request.get_json()
    success = node.add_transaction(transaction_dict, blockchain)
    if success:
        return jsonify(''), 200
    else:
        return jsonify('invalid transaction'), 400

# Endpoint where other members send us the blocks they have mined
@app.route('/block', methods=['POST'])
def post_block():
    block_dict = request.get_json()
    valid = node.valid_proof(block_dict, blockchain)   
    if valid:
        block = Block.from_dict(block_dict)
        blockchain.blocks.append(block)
        return jsonify(''), 200
    else:
        return jsonify('invalid block'), 400

# Endpoint for the coordinator where members send us their info
@app.route('/register', methods=['POST'])
def register_member():
    member_ip = request.remote_addr
    data = request.get_json()
    
    port = data['port']
    public_key = data['public_key']
    
    # Add memeber's info to our dictionary
    next_id = node.register_node_to_network(public_key, member_ip, port)

    # Send current blockchain to new member
    requests.post(f'http://{member_ip}:{port}/blockchain', json=blockchain.to_dict())

    # Send 100 NBC to new member
    node.broadcast_transaction(node.wallet.public_key, public_key, 100)

    # After all members have registered broadcast the network's details
    if len(node.network) == node.no_of_nodes:
        node.broadcast_network_info()

    # Send id back to member that has been registered
    response = {'id': next_id}
    return jsonify(response), 200

# Endpoint for the members where the coordinator sends us the network info
@app.route('/members', methods=['POST'])
def post_memebers():
    node.network = request.get_json()
    return jsonify(''), 200

# Coordinator code. Create genesis tranasction and block that don't get validated
@app.route('/initialize/coordinator', methods=['POST'])
def post_init_coordinator():
    data = request.get_json()
    node.no_of_nodes = data['members']
    node.register_node_to_network(node.wallet.public_key, COORDINATOR_IP, COORDINATOR_PORT)

    genesis_transaction = Transaction(0, node.wallet.public_key, 100 * node.no_of_nodes)
    node.sign_transaction(genesis_transaction)
    list_of_transactions = [genesis_transaction]

    genesis_block = Block(0, list_of_transactions, 1, 0)
    blockchain.utxos[node.wallet.public_key] = []
    blockchain.utxos[node.wallet.public_key].append(
            Transaction_Output(genesis_transaction.id, node.wallet.public_key, genesis_transaction.amount))

    blockchain.blocks.append(genesis_block)

    return jsonify(''), 200

# Member code. Register self to coordinator and receive network id
@app.route('/initialize/member', methods=['GET'])
def post_init_member():
    data = {'port': FLASK_PORT, 'public_key': node.wallet.public_key}
    response = requests.post(f'http://{COORDINATOR_IP}:{COORDINATOR_PORT}/register', json=data)
    node.id = response.json()['id']
    return jsonify(''), 200

# Run it once fore every node
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int,
        help='port to listen on')
    args = parser.parse_args()
    FLASK_PORT = args.port

    app.run(host='127.0.0.1', port=FLASK_PORT)
