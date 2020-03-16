import requests
from cmd import Cmd

class Prompt(Cmd):

    def __init__(self, backend_url):
        super().__init__()
        self.backend_url = backend_url

    def do_t(self, args):
        """t <recipient_address> <amount>\nSends <amount> NBC to the <recipient_address>"""
        if len(args) != 2:
            print('Usage: t <recipient_address> <amount>')
            return

        recipient_address = args[0]
        amount = int(args[1])
        dictionary = {'recipient_address': recipient_address,
                      'amount': amount}
        response = requests.post(self.backend_url + 'transaction/local', json=dictionary)
        status = response.json()['status']
        print('Transaction status:', status)

    def do_view(self, args):
        """Fetch the latest valid block's transactions"""
        response = requests.get(self.backend_url + 'block')
        list_of_transactions = response.json()['list_of_transactions']

        print('Transactions:')
        for transaction in list_of_transactions:
            print('Transaction: From ->\n', transaction['sender_address'],
                  '\nTo ->\n', transaction['recipient_address'],
                  '\nAmount-> ', transaction['amount'], '\n', sep='')


    def do_balance(self, args):
        """Returns the balance of wallet"""
        response = requests.get(self.backend_url + 'balance')
        balance = response.json()['balance']
        print('Current wallet balance is:', balance, 'NBC')

    def do_quit(self, args):
        """Quits the program"""
        print('Quitting...')
        raise SystemExit

    def default(self, args):
        self.do_help('')

    def do_EOF(self, args):
        """Hit ^D to quit the program"""
        print('\nQuitting...')
        return True
