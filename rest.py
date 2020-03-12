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
blockchain = Blockchain()
node = Node()


#.......................................................................................

# New incoming transaction
@app.route('/transaction', methods=['POST'])
def post_transaction():
    return jsonify(response), 200

# Nonce for new block found
@app.route('/block', methods=['POST'])
def post_block():
    return jsonify(response), 200

# New member sent his info - Coordinator only
@app.route('/register', methods=['POST'])
def register_member():
    member_ip = request.remote_addr
    data = request.json
    port = data['port']
    public_key = data['public_key']
    
    # Add memeber's info to our dictionary
    node.register_node_to_network(public_key, member_ip, port)

    # Send blockchain to member
    data = blockchain.to_dict()
    requests.post(f'{member_ip}/block', data)

    # Send 100 NBC to member
    node.broadcast_transaction(node.wallet.public.key, public_key, 100)

    response = {'id': next_id}
    return jsonify(response), 200

# Coordinator sent the list of nodes - Member only
@app.route('/members', methods=['POST'])
def post_memebers():
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

    # Coordinator code
    if (node_type.lower().startswith('c')):
        node.register_node_to_network(node.wallet.public_key, host, port)

        genesis_transaction = Transaction(0, node.wallet.public_key, 100 * members)
        genesis_block = Block(0, genesis_transaction, 1, 0)
        Blockchain.blocks.append(genesis)
    # Member code
    else:
        data = {'port': port, 'public_key': node.wallet.public_key}
        response, status = requests.post(f'{host}:{port}/register', data)
        node.id = response['id']

    app.run(host='127.0.0.1', port=port)
