import requests
from argparse import ArgumentParser
from prompt import Prompt

parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5000, type=int,
        help='port that flask listens to')
parser.add_argument('-t', '--type', default='member', type=str,
        help='type of node: "coordinator" or "member"')
parser.add_argument('-m', '--members', default='5', type=int,
        help='number of members of the network used from the coordinator')
parser.add_argument('-f', '--file', default='', type=str,
        help='file that will be used to automatically send transactions')

args = parser.parse_args()
port = args.port
node_type = args.type
members = args.members
file_ = args.file

backend_url = f'http://127.0.0.1:{port}/'

# Initialize backend by creating the genesis block or connecting to the coordinator
if (node_type.lower().startswith('c')):
    data = {'members': members} 
    response = requests.post(backend_url + 'initialize/coordinator', json=data)
    if response.status_code != 200:
        print('Coordinator initialization failed')
        raise SystemExit
    node_id = 0
else:
    response = requests.get(backend_url + 'initialize/member')
    if response.status_code != 200:
        print('Member initialization failed')
        raise SystemExit
    node_id = response.json()['id_']

if file_ != '':
    # Files read have this format `id0 2`
    with open(file_, 'r') as f:
        for line in f:
            tokens = line.split()
            recipient_id = int(tokens[0][2])
            amount = int(tokens[1])
            dictionary = {'recipient_id': recipient_id,
                          'amount': amount}
            requests.post(self.backend_url + 'transaction/local', json=dictionary)

prompt = Prompt(backend_url)
prompt.prompt = '> '
prompt.cmdloop()
