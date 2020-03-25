import requests
from cmd import Cmd

class Prompt(Cmd):

    def __init__(self, backend_url, my_id):
        super().__init__()
        self.backend_url = backend_url
        self.my_id = my_id

    def do_t(self, line):
        """t <recipient_id> <amount>\nSends <amount> NBC to the <recipient_id>"""
        tokens = line.split()
        if len(tokens) != 2:
            print('Usage: t <recipient_id> <amount>')
            return
       
        try:
            recipient_id = int(tokens[0])
            amount = int(tokens[1])
        except ValueError:
            print('Invalid id or amount')
            return

        dictionary = {'recipient_id': recipient_id,
                      'amount': amount}
        response = requests.post(self.backend_url + 'transaction/local', json=dictionary)

        status = response.json()['status']
        print('Transaction status:', status)

    def do_view(self, line):
        """Fetch the latest valid block's transactions"""
        response = requests.get(self.backend_url + 'block')
        list_of_transactions = response.json()['list_of_transactions']

        print('Transactions:')
        for transaction in list_of_transactions:
            print('Transaction: From ->\n', transaction['sender_address'],
                  '\nTo ->\n', transaction['recipient_address'],
                  '\nAmount-> ', transaction['amount'], '\n', sep='')

    def do_viewall(self, line):
        """Fetch all the transactions"""
        response = requests.get(self.backend_url + 'blockchain')
        blocks = response.json()['blocks']
        for block in blocks:
            list_of_transactions = block['list_of_transactions']
            for transaction in list_of_transactions:
                print('Transaction: From ->\n', transaction['sender_address'],
                  '\nTo ->\n', transaction['recipient_address'],
                  '\nAmount-> ', transaction['amount'], '\n', sep='')

    def do_balance(self, line):
        """Returns the balance of wallet"""
        response = requests.get(self.backend_url + 'balance')
        balance = response.json()['balance']
        print('Current wallet balance is:', balance, 'NBC')

    def do_transactions(self, line):
        """Executes the transactions in the given folder using the local id
        Usage: transactions <transactions_folder>
        The input file used inside the folder is of the format `transactions<id>.txt`"""
        input_file = line + '/transactions' + str(self.my_id) + '.txt'
        with open(input_file, 'r') as f:
            for line in f:
                tokens = line.split()
                recipient_id = int(tokens[0][2])
                amount = int(tokens[1])
                dictionary = {'recipient_id': recipient_id,
                              'amount': amount}
                requests.post(self.backend_url + 'transaction/local', json=dictionary)

    def do_stats(self, line):
        """Requests stats from the backend"""
        response = requests.get(self.backend_url + 'stats')
        if response.status_code == 200:
            dictionary = response.json()
            total_transactions = dictionary['total_transactions']
            throughput = dictionary['throughput']
            mine_time = dictionary['mine_time']
            print("Total transactions:", total_transactions, "Throughput:", throughput, "Average mine time:", mine_time)
        else:
            print("There are still pending transactions")

    def do_quit(self, line):
        """Quits the program"""
        print('Quitting...')
        raise SystemExit

    def default(self, line):
        self.do_help('')

    def do_EOF(self, line):
        """Hit ^D to quit the program"""
        print('\nQuitting...')
        return True
