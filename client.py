import requests
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int,
        help='port that flask listens to')
parser.add_argument('-t', '--type', default='member', type=str,
        help='type of node: "coordinator" or "member"')
parser.add_argument('-m', '--members', default='5', type=int,
        help='number of members of the network used from the coordinator')

args = parser.parse_args()
port = args.port
node_type = args.type
members = args.members

if (node_type.lower().startswith('c')):
    data = {'members': members} 
    requests.post(f'http://127.0.0.1:{port}/initialize/coordinator', json=data)
else:
    requests.get(f'http://127.0.0.1:{port}/initialize/member')
