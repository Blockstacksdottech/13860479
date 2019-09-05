from web3 import Web3,HTTPProvider
from .settings import *
from web3.middleware import geth_poa_middleware
from .models import *
from .nodes_handler import *
from .binance_handler import *




def get_address_transactions(address,w):
	i = w.eth.getBlock('latest').number 
	while i >= 0:
		#print(str(i))
		block = w.eth.getBlock(i,full_transactions=True)
		for transaction in block.transactions:
			to = transaction['to']
			if to == address:
				hs = transaction['hash']
				b_num = transaction['blockNumber']
				lat = w.eth.getBlock('latest').number
				print('confirmations : ',end=' ')
				confirmations = lat-b_num
				print(confirmations)

				return [hs,confirmations]
				
		i -= 1



# linear script

class listener:
	def __init__(self,coin,private,idd):
		self.transaction_id = idd
		self.transaction = Transaction.objects.filter(transaction_id = idd)[0]
		self.b_handler = Handler()
		if coin == 'ETH':
			self.w = Web3(HTTPProvider('http://23.254.176.26:8546'))
			self.w.middleware_onion.inject(geth_poa_middleware, layer=0)
			self.account  = self.w.eth.account.privateKeyToAccount(private)
			#self.start_ethereum()
		elif coin == 'BTC':
			self.handler = get_handler(coin)
			self.address = private
		elif coin == 'LTC':
			self.handler = get_handler(coin)
			self.address = private
		elif coin  == 'BCH':
			self.handler = get_handler(coin)
			self.address = private

	
	def get_second_handler(self,coin):
		if coin == 'ETH':
			self.w2 = Web3(HTTPProvider('http://23.254.176.26:8546'))
			self.w2.middleware_onion.inject(geth_poa_middleware, layer=0)
			return self.w2
			#self.account  = self.w2.eth.account.privateKeyToAccount(master_eth_private)
			#self.start_ethereum()
		elif coin == 'BTC':
			self.handler2 = get_handler(coin)
			return self.handler2
			#self.address = private
		elif coin == 'LTC':
			self.handler2 = get_handler(coin)
			return self.handler2

	
	def set_transaction_message(self,idd,message,status="not yet"):
		task = Task.objects.filter(transaction_id = idd)[0]
		task.status = status
		task.action = message
		task.save()





	def check_balance(self,balance):
		if balance == 0:
			return True
		else:
			return False

	def get_eth_confirmation(self,hsh):
		return self.w.eth.getBlock('latest').number -  self.w.eth.getTransaction(hsh).blockNumber
	
	def create_eth_transaction(self,to):
		value = self.w.eth.getBalance(self.account.address) - (100000 * self.w.eth.gasPrice)
		signed_txn = self.w.eth.account.signTransaction(dict(
				nonce=self.w.eth.getTransactionCount(self.account.address,'pending'),
				gasPrice=self.w.eth.gasPrice,
				gas=100000,
				to=to,
				value=value,
				data=b'',
			),
			self.account.privateKey,
			)
		return signed_txn
	
	def create_eth_transaction_cus(self,to,value,private,w,address):
		signed_txn = w.eth.account.signTransaction(dict(
				nonce=w.eth.getTransactionCount(address,'pending'),
				gasPrice=w.eth.gasPrice,
				gas=100000,
				to=to,
				value=value,
				data=b'',
			),
			private,
			)
		return signed_txn

	
	def get_transaction(self,address,trs):
		for tr in trs:
			if tr['address'] == address:
				return tr['txid']
			else:
				pass
		
		return False

	def get_confirmations(self,txid):
		tr = self.handler.send('gettransaction',txid)
		return tr['confirmations']


	def start_listener(self):
		print('start check')
		print(self.address)
		while self.check_balance(self.handler.send('getreceivedbyaddress',self.address)):
			pass
		print('balance changed')
		print('getting txid')
		txid = self.get_transaction(self.address,self.handler.send('listtransactions',main_test_label))
		self.set_transaction_message(self.transaction_id,'checking confirmations')
		while self.get_confirmations(txid) < min_confirmation:
			pass
		print('transaction confirmed')
		self.set_transaction_message(self.transaction_id,'checking availability')
		print('received')
		amount_in = self.handler.send('getreceivedbyaddress',self.address)
		print('getting the out value')
		
		second_handler = self.get_second_handler(self.transaction.out_currency)

		amount_out = self.b_handler.get_exchange_rate(self.transaction.in_currency,self.transaction.out_currency,self.transaction.fees,amount_in)
		amount_out +=  float(Web3.fromWei(second_handler.eth.gasPrice * 100000,'ether'))
		print('the amount out is ')
		print(amount_out)
		self.transaction.amount_in = amount_in
		self.transaction.amount_out = amount_out
		self.transaction.save()
		if 'ETH' == self.transaction.out_currency:
			balance =float(Web3.fromWei(self.w2.eth.getBalance(eth_test_provider_ad),'ether'))
		elif 'BTC' == self.transaction.out_currency:
			balance = self.handler2.send('getbalance')
		elif 'LTC' == self.transaction.out_currency:
			balance = self.handler2.send('getbalance')
		
		if amount_out >= balance:
			input('not enough balance')
		else:
			if 'ETH' == self.transaction.out_currency:
				amount_out  = Web3.toWei(amount_out,'ether')
				print('sending the amount to ' + self.transaction.return_address)
				signed_txn = self.create_eth_transaction_cus(self.transaction.return_address,amount_out,eth_test_provider_p,second_handler,eth_test_provider_ad)
				second_handler.eth.sendRawTransaction(signed_txn.rawTransaction)
				print('transaction sent')

			elif 'LTC'  == self.transaction.out_currency:
				print('sending')
				amount_out = round(amount_out,8)
				print('sending amount : ',end=' ')
				print(amount_out)
				res = self.handler2.send('sendtoaddress',self.transaction.return_address,amount_out)
				if not res:
					print('failed')
				self.set_transaction_message(self.transaction_id,'transaction sent','done')
			else:
				print('sending')
				amount_out = round(amount_out,8)
				print('sending amount : ',end=' ')
				print(amount_out)
				self.handler2.send('sendtoaddress',self.transaction.return_address,amount_out)
				self.set_transaction_message(self.transaction_id,'transaction sent','done')
		


	def start_c(self,coin):
		if coin  == 'ETH':
			self.start_ethereum()
		else:
			self.start_listener()
			

		




		


	

	def start_ethereum(self):
		print('start checking')
		print(self.account.address)
		while self.check_balance(self.w.eth.getBalance(self.account.address)):
			pass
		print('balance changed')
		print('getting block hash')
		self.set_transaction_message(self.transaction_id,'checking confirmations')
		res = get_address_transactions(self.account.address,self.w)
		confirmation = res[-1]
		while confirmation <  min_confirmation:
			confirmation = self.get_eth_confirmation(res[0])
			#print(confirmation)
		print('transaction  confirmed')
		print('balance')
		amount_in = float(Web3.fromWei(self.w.eth.getBalance(self.account.address),'ether'))   
		print(amount_in)
		
		print('resending to the master accout')
		print(master_eth_add)
		signed_txn = self.create_eth_transaction(master_eth_add)
		self.w.eth.sendRawTransaction(signed_txn.rawTransaction)
		print('sent  to master add')
		self.set_transaction_message(self.transaction_id,'checking availability')
		print('received')
		amount_out = self.b_handler.get_exchange_rate(self.transaction.in_currency,self.transaction.out_currency,self.transaction.fees,amount_in)
		print('amount out is ')
		print(amount_out)
		self.transaction.amount_in = amount_in
		self.transaction.amount_out = amount_out
		self.transaction.save()
		second_handler = self.get_second_handler(self.transaction.out_currency)
		if 'ETH' == self.transaction.out_currency:
			balance =float(Web3.fromWei(self.w2.eth.getBalance(eth_test_provider_ad),'ether'))
		elif 'BTC' == self.transaction.out_currency:
			balance = self.handler2.send('getbalance')
		elif 'LTC' == self.transaction.out_currency:
			balance = self.handler2.send('getbalance')
		if amount_out >= balance:
			input('not enough balance')
		elif 'LTC'  == self.transaction.out_currency:
			print('sending')
			amount_out = round(amount_out,8)
			print('sending amount : ',end=' ')
			print(amount_out)
			res = self.handler2.send('sendtoaddress',self.transaction.return_address,amount_out)
			if not res:
				print('failed')
			self.set_transaction_message(self.transaction_id,'transaction sent','done')

		else:
			print('sending')
			amount_out = round(amount_out,8)
			print('sending amount : ',end=' ')
			print(amount_out)
			self.handler2.send('sendtoaddress',self.transaction.return_address,amount_out)
			self.set_transaction_message(self.transaction_id,'transaction sent','done')




# test
"""
print('starting')
w = Web3(HTTPProvider('http://23.254.176.26:8546'))
w.middleware_onion.inject(geth_poa_middleware, layer=0)
#acc = w.eth.account.create('hello')
#print(acc.address)
#print(acc.privateKey)
pv = b'\xb9\x13$\xf8\xa2\xa8\x81!\xa4rW\x81\x8b\xf8\xe0\x1b\xf1\xfdMUS\xd4M\\\x85\xdb\xaf\x86\xf6Q\x05\xf5'
print('##########')
lst = listener('ETH',pv)
"""


		





