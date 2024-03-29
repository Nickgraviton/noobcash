# Distributed Systems 2019-2020 Assignment
Simple blockchain implementation in python
## Project Structure
```
├── backend
│   ├── blockchain.py
│   ├── block.py
│   ├── node.py
│   ├── properties.py
│   ├── rest.py
│   ├── transaction.py
│   └── wallet.py
├── client
│   ├── client.py
│   └── prompt.py
├── README.md
└── requirements.txt
```
##### Back end:
* `blockchain.py:` Specifies the Blockchain class that holds the blocks and the transactions
* `block.py:` Specifies the Block class that holds transaction info along with its hash, the hash of the previous block and the nonce used for the proof of work
* `node.py:` Holds the nodes id along with info of every other node. Most functions such as mining, signing or broadcasting are performed through the Node class
* `properties.py:` Holds the proof of work difficulty, block transaction capacity and coordinator info constants
* `rest.py:` Specifies a REST API running with Flask and defines the endpoints where the nodes will exchange data
* `transaction.py:` Specifies the Transaction class that holds the tranasaction details like the sender address, the recipient address, the amount of the transaction, the hash of the transaction, its inputs and its outputs and the Transaction Output class that holds information about the output of a transaction
* `wallet.py:` Specifies a Wallet class that holds the private and public key of the wallet using the RSA algorithm to generate those keys
##### Client:
* `client.py:` This class is responsible for handling user requests and initializing the blockchain after the Flask server has started by sending an init request to the local server
* `prompt.py:` This class provides a CLI supporting a few user operations specifically:
    * `t <recipient_address> <amount>:` Sends amount Noobcash Coins(NBC) to the recipient address
    * `transactions <transactions_folder>:` Issues the transactions inside the specified folder. It searches for files of the format transactions<local_id>.txt
    * `view:` Prints out the details of all the transactions in the last validated block in the blockchain
    * `viewall:` Prints out the details of all the transactions in the blockchain
    * `balance:` Prints out the wallet's current balance
    * `help:` Explains what each command does if given an argument or provides a list of available commands when no argument is supplied
    * `stats:` Prints if mining has finished, the number of pending transactions, throughput and average time a block needs to be added to the chain
    * `EOF/quit:` Exits the client CLI

`requirements.txt:` Python package requirements

## How to run
Optional: Change the values in the properties file to specify the difficulty of the proof of work, the capacity of each block and the IP/port that the coordinator will use
1. Set up a virtual environment:`python3 -m venv .venv`
2. Activate the virtual environment: `source .venv/bin/activate`
3. Install the requirements: `pip3 install -r requirements.txt`
4. Run the flask server on each node: `python3 backend/rest.py -i <IP_that_will_host_the_flask_server> -p <local_flask_port>`
5. Run `client.py` on one node as a coordinator: `python3 client/client.py -i <IP_that_hosts_the_flask_server> -p <local_flask_port> -t coordinator -m <number_of_members_in_the_network>` (The IP and port need to be the same as the ones in the properties file so that others know how to connect to the network)
6. Run `client.py` on all other nodes as members: `python3 client/client.py -i <IP_that_hosts_the_flask_server> -p <local_flask_port>`
7. Issue commands on the client CLI
