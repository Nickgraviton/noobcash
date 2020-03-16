import requests
from backend.block import Block
from cmd import Cmd

class Prompt(Cmd):

    def __init__(self, backend_url):
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
        response = requests.post(self.backend_url + 'transaction/local')
        status = response.json()['status']
        print('Transaction status:', status)

    def do_view(self, args):
        """Fetch the latest valid block's transactions"""
        response = requests.get(self.backend_url + 'block')
        block_dict = response.json()
        block = Block.from_dict(block_dict)

        print('Transactions:')
        for transaction in block.list_of_transactions:
            print('Transaction: From ->', transaction.sender_address,
                  '\nTo ->', transaction.recipient_address,
                  '\nAmount->', transaction.amount, '\n')


    def do_balance(self, args):
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
