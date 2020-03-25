import requests
from argparse import ArgumentParser
from prompt import Prompt

parser = ArgumentParser()
parser.add_argument('-i', '--ip', default='127.0.0.1', type=str,
        help='IP that hosts the flask server')
parser.add_argument('-p', '--port', default=5000, type=int,
        help='port that flask listens to')
parser.add_argument('-t', '--type', default='member', type=str,
        help='type of node: "coordinator" or "member"')
parser.add_argument('-m', '--members', default='5', type=int,
        help='number of members of the network used from the coordinator')

args = parser.parse_args()
ip = args.ip
port = args.port
node_type = args.type
members = args.members

backend_url = 'http://{}:{}/'.format(ip, port)

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

prompt = Prompt(backend_url, node_id)
prompt.prompt = '> '
prompt.cmdloop()
