import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

import block
import node
import blockchain
import wallet
import transaction
import wallet

app = Flask(__name__)
CORS(app)

# Create the blockchain and initialize the node
blockchain = Blockchain()
node = Node()

#--------------------------------------------------------------------
#------------------------------REST API------------------------------
#--------------------------------------------------------------------

# Special endpoint for receiving the genesis block
@app.route('/genesis', methods=['POST'])
def post_genesis():
    blockchain_dict = request.json
    blockchain.blocks = blockchain_dict['blocks']
    blockchain.transactions = blockchain_dict['transactions']
    blockchain.utxos = blockchain_dict['utxos']
    return jsonify(''), 200

# New incoming transaction
@app.route('/transaction', methods=['POST'])
def post_transaction():
    transaction_dict = request.json
    node.add_transaction(transaction_dict, blockchain)
    return jsonify(''), 200

# Nonce for new block found
@app.route('/block', methods=['POST'])
def post_block():
    block_dict = request.json
    node.valid_proof(block_dict, blockchain)   
    return jsonify(''), 200

# New member sent his info - Coordinator only
@app.route('/register', methods=['POST'])
def register_member():
    member_ip = request.remote_addr
    data = request.json
    port = data['port']
    public_key = data['public_key']
    
    # Add memeber's info to our dictionary
    next_id = node.register_node_to_network(public_key, member_ip, port)

    # Send current blockchain to new member
    requests.post(f'{member_ip}/genesis', blockchain.to_dict())

    # Send 100 NBC to new member
    node.broadcast_transaction(node.wallet.public.key, public_key, 100)

    # After all members have registered broadcast the network's details
    if len(node.network) == node.no_of_nodes:
        node.broadcast_network_info()

    # Send id back to member that has been registered
    response = {'id': next_id}
    return jsonify(response), 200

# Coordinator sent the list of nodes - Member only
@app.route('/members', methods=['POST'])
def post_memebers():
    node.network = request.json
    return jsonify(response), 200


# Run it once fore every node
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-h', '--host', default='192.168.1.1', type=str,
            help='IP address of the coordinator')
    parser.add_argument('-p', '--port', default=5000, type=int,
            help='port to listen on')
    parser.add_arguemnt('-t', '--type', default='member', type=str,
            help='type of node: "coordinator" or "member"')
    parser.add_arguemnt('-m', '--members', default='5', type=int,
            help='number of members of the network')

    args = parser.parse_args()
    host = args.host
    port = args.port
    node_type = args.type
    members = args.members

    # Coordinator code. Create genesis tranasction and block that don't get validated
    if (node_type.lower().startswith('c')):
        node.no_of_nodes = members
        node.register_node_to_network(node.wallet.public_key, host, port)

        genesis_transaction = Transaction(0, node.wallet.public_key, 100 * members)
        node.sign_transaction(genesis_transaction)
        genesis_block = Block(0, genesis_transaction, 1, 0)
        blockchain.utxos[node.wallet.public_key] = Transaction_Output(genesis_transaction.id,
                node.wallet.public_key, genesis_transaction.amount)
        blockchain.blocks.append(genesis)
    # Member code. Register self to coordinator and receive network id
    else:
        data = {'port': port, 'public_key': node.wallet.public_key}
        response, status = requests.post(f'{host}:{port}/register', data)
        node.id = response['id']

    app.run(host='127.0.0.1', port=port)
