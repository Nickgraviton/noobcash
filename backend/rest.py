import threading
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from properties import COORDINATOR_IP, COORDINATOR_PORT, CAPACITY
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
node.miner = threading.Thread(target=node.mine_block, args=[blockchain])
node.miner.start()

#--------------------------------------------------------------------
#------------------------------REST API------------------------------
#--------------------------------------------------------------------

# Endpoint where the client can ask for the wallet's balance
@app.route('/balance', methods=['GET'])
def get_balance():
    balance = node.wallet.balance(blockchain, node.wallet.public_key)
    response = {'balance': balance}
    return jsonify(response), 200

# Endpoint where other members can request our blockchain
@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    blockchain_dict = blockchain.to_dict()
    return jsonify(blockchain_dict), 200

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
@app.route('/transaction/remote', methods=['POST'])
def post_transaction_remote():
    transaction_dict = request.get_json()
    success = node.add_transaction(transaction_dict, blockchain)
    if success:
        return jsonify(''), 200
    else:
        return jsonify('invalid transaction'), 400

# Endpoint where the local client can send us transactions to broadcast
@app.route('/transaction/local', methods=['POST'])
def post_transaction_local():
    transaction_dict = request.get_json()

    recipient_address = None
    # Support both id and address of recipient
    if 'recipient_address' in transaction_dict:
        recipient_address = transaction_dict['recipient_address']
    else:
        recipient_id = transaction_dict['recipient_id']
        for n, info in node.network.items():
            if info['id_'] == recipient_id:
                recipient_address = n
    if recipient_address is None:
        return jsonify({'status': 'fatal error'}), 400

    amount = transaction_dict['amount']

    success = node.create_transaction(recipient_address, amount, blockchain)
    if success:
        return jsonify({'status': 'transaction successful'}), 200
    else:
        return jsonify({'status': 'transaction unsuccessful'}), 400

# Endpoint where the client can request the latest validated block
@app.route('/block', methods=['GET'])
def get_block():
    last_block = blockchain.blocks[-1]
    list_of_transactions = [t.to_dict() for t in last_block.list_of_transactions]
    transaction_dict = {'list_of_transactions': list_of_transactions}
    return jsonify(transaction_dict), 200

# Endpoint where other members send us the blocks they have mined
@app.route('/block', methods=['POST'])
def post_block():
    block_dict = request.get_json()
    block = Block.from_dict(block_dict)
    status = node.valid_proof(block, blockchain)

    if status == 'success':
        to_be_removed = []
        for transaction in block.list_of_transactions:
            if transaction.id_  in blockchain.transactions_set:
                return jsonify('block transaction already added'), 400

            # Add transaction if we don't already have it
            node.add_transaction(transaction.to_dict(), blockchain, part_of_block=True)
            for t in blockchain.transactions:
                if t.id_ == transaction.id_:
                    to_be_removed.append(t)

        # Remove transactions in the received block from our pending ones
        with blockchain.lock:
            for transaction in block.list_of_transactions:
                blockchain.transactions_set.add(transaction.id_)
            for transaction in to_be_removed:
                blockchain.transactions.remove(transaction)

            blockchain.blocks.append(block)

        return jsonify(status), 200
    else:
        return jsonify(status), 400

# Endpoint for the coordinator where members send us their info
@app.route('/register', methods=['POST'])
def register_member():
    member_ip = request.remote_addr
    # If process is on the same node as the coordinator we use the coordinator IP
    if member_ip == '127.0.0.1':
        member_ip = COORDINATOR_IP
    data = request.get_json()
    
    port = data['port']
    public_key = data['public_key']
    
    # Add memeber's info to our dictionary
    next_id = node.register_node_to_network(public_key, member_ip, port)

    # Send current blockchain to new member
    requests.post('http://{}:{}/blockchain'.format(member_ip, port), json=blockchain.to_dict())

    # Send 100 NBC to new member
    node.create_transaction(public_key, 100, blockchain)

    # After all members have registered broadcast the network's details
    if len(node.network) == node.no_of_nodes:
        node.broadcast_network_info()

    # Send id back to member that has been registered
    response = {'id_': next_id}
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
            Transaction_Output(genesis_transaction.id_, node.wallet.public_key, genesis_transaction.amount))

    blockchain.blocks.append(genesis_block)

    return jsonify(''), 200

# Member code. Register self to coordinator and receive network id
@app.route('/initialize/member', methods=['GET'])
def post_init_member():
    data = {'port': FLASK_PORT, 'public_key': node.wallet.public_key}
    response = requests.post('http://{}:{}/register'.format(COORDINATOR_IP, COORDINATOR_PORT), json=data)
    node.id_ = response.json()['id_']

    info = {'id_': node.id_}
    return jsonify(info), response.status_code

# Return the transaction throughput and average mine time
@app.route('/stats', methods=['GET'])
def get_stats():
    # Return a success status only if there are no pending transactions
    if not blockchain.transactions:
        total_time = blockchain.blocks[-1].timestamp - blockchain.blocks[0].list_of_transactions[0].timestamp
        total_transactions = len(blockchain.blocks) * CAPACITY
        throughput = total_transactions / total_time

        average_mine_time = node.mine_time / node.mine_counter

        response = {'total_transactions': total_transactions,
                    'throughput': throughput,
                    'mine_time': average_mine_time}
        return jsonify(response), 200
    else:
        return jsonify(''), 400
    

# Run it once fore every node
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--ip', default='127.0.0.1', type=str,
        help='IP to host the flask server')
    parser.add_argument('-p', '--port', default=5000, type=int,
        help='port to listen on')
    args = parser.parse_args()
    ip = parser.ip
    FLASK_PORT = args.port

    app.run(host=ip, port=FLASK_PORT)
