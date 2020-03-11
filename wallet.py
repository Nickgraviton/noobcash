import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

class Wallet:

	def __init__(self):
		##set
		#self.public_key
		#self.private_key
		#self_address
		#self.transactions

		# Initializations:
		# RSA length is 1024 bits, so it can be fast and secure enough, but it can also be 2048 ..
		# ..(more secure, still multiple of 256)
		self.private_key = RSA.generate(1024, Crypto.Random.new().read)
		# Create the public key according to the private key
		self.public_key = self.private_key.publickey()
		# print(self.private_key)
		# print(type(self.private_key))
		
		#self.address = self.public_key

	def balance():
		return 100

	def get_public_key(self, format='string'):
		if (format == 'string'):
			return binascii.hexlify(self.public_key.exportKey(format='DER')).decode('ascii')
			# return self.public_key.exportKey(format='OpenSSH')
		elif (format == 'none'): 
			return self.public_key
		else:
			print("Wrong format. Returning string.")
			return binascii.hexlify(self.wallet.public_key.exportKey(format='DER')).decode('ascii')

# υπο εξεταση η balance και μαλλον δε χρειαζονται οι γραμμες 40-44, ολα τα αλλα σωστα απο το τουτοριαλ
#ισως να χρειαζεται και η γραμμη 31, το βλεπουμε με βαση τα παρακατω
