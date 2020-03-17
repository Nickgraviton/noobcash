import requests
from cmd import Cmd

class Prompt(Cmd):

    def __init__(self, backend_url):
        super().__init__()
        self.backend_url = backend_url

    def do_t(self, line):
        """t <recipient_id> <amount>\nSends <amount> NBC to the <recipient_id>"""
        tokens = line.split()
        if len(tokens) != 2:
            print('Usage: t <recipient_id> <amount>')
            return
        
        # Input id is of the form `id0`
        recipient_id = int(tokens[0][2])
        amount = int(tokens[1])
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


    def do_balance(self, line):
        """Returns the balance of wallet"""
        response = requests.get(self.backend_url + 'balance')
        balance = response.json()['balance']
        print('Current wallet balance is:', balance, 'NBC')

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
