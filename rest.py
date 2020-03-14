import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from block import Block
from node import Node
from blockchain import Blockchain
from transaction import Transaction, Transaction_Output

app = Flask(__name__)
CORS(app)

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
    blockchain_dict = request.json
    blocks = blockchain_dict['blocks']
    transactions = blockchain_dict['transactions']
    utxos = blockchain_dict['utxos']

    # Empty blockchain in our node so far which means the coordinator
    # sent us the current blockchain
    if not blockchain.blocks:
        valid = node.valid_chain(blocks, blockchain)
        if not valid:
            return jsonify('invalid block'), 400
        blockchain.blocks = blocks
        blockchain.transactions = transactions
        blockchain.utxos = utxos
    return jsonify(''), 200

# Endpoint where other members send us transactions
@app.route('/transaction', methods=['POST'])
def post_transaction():
    transaction_dict = request.json
    node.add_transaction(transaction_dict, blockchain)
    return jsonify(''), 200

# Endpoint where other members send us the blocks they have mined
@app.route('/block', methods=['POST'])
def post_block():
    block_dict = request.json
    valid = node.valid_proof(block_dict, blockchain)   
    if valid:
        timestamp = block_dict['timestamp']
        index = block_dict['index']
        list_of_transactions = block_dict['list_of_transactions']
        previous_hash = block_dict['previous_hash']
        nonce = block_dict['nonce']

        block = Block(index, list_of_transactions, previous_hash, nonce, timestamp)
        blockchain.blocks.append(block)
    return jsonify(''), 200

# Endpoint for the coordinator where members send use their info
@app.route('/register', methods=['POST'])
def register_member():
    member_ip = request.remote_addr
    data = request.json
    port = data['port']
    public_key = data['public_key']
    
    # Add memeber's info to our dictionary
    next_id = node.register_node_to_network(public_key, member_ip, port)

    # Send current blockchain to new member
    requests.post(f'http://{member_ip}/block', blockchain.to_dict())

    # Send 100 NBC to new member
    node.broadcast_transaction(node.wallet.public.key, public_key, 100)

    # After all members have registered broadcast the network's details
    if len(node.network) == node.no_of_nodes:
        node.broadcast_network_info()

    # Send id back to member that has been registered
    response = {'id': next_id}
    return jsonify(response), 200

# Endpoint for the members where the coordinator sends us the network info
@app.route('/members', methods=['POST'])
def post_memebers():
    node.network = request.json
    return jsonify(response), 200


# Run it once fore every node
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-c', '--coordinator', default='192.168.1.1', type=str,
            help='IP address of the coordinator')
    parser.add_argument('-p', '--port', default=5000, type=int,
            help='local port to listen on')
    parser.add_argument('-t', '--type', default='member', type=str,
            help='type of node: "coordinator" or "member"')
    parser.add_argument('-m', '--members', default='5', type=int,
            help='number of members of the network used from the coordinator')

    args = parser.parse_args()
    coordinator = args.coordinator
    port = args.port
    node_type = args.type
    members = args.members

    # Coordinator code. Create genesis tranasction and block that don't get validated
    if (node_type.lower().startswith('c')):
        node.no_of_nodes = members
        node.register_node_to_network(node.wallet.public_key, coordinator, port)

        genesis_transaction = Transaction(0, node.wallet.public_key, 100 * members)
        node.sign_transaction(genesis_transaction)
        genesis_block = Block(0, [genesis_transaction], 1, 0)
        blockchain.utxos[node.wallet.public_key] = []
        blockchain.utxos[node.wallet.public_key].append(
                Transaction_Output(genesis_transaction.id, node.wallet.public_key, genesis_transaction.amount))
        blockchain.blocks.append(genesis_block)
    # Member code. Register self to coordinator and receive network id
    else:
        data = {'port': port, 'public_key': node.wallet.public_key}
        response, status = requests.post(f'http://{coordinator}:{port}/register', data)
        node.id = response['id']

    app.run(host='127.0.0.1', port=port)
