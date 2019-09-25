from binance.client import Client
from web3 import Web3
from .settings import *
from .models import  *
from .nodes_handler import *
from .binance_handler import *
import ccxt


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


class worker:
	def __init__(self):
		self.client = Client(b_a_k,b_a_p)
		self.coins_list =  ['ETH','BTC','BCH','XMR','LTC']
		self.c = Client(b_a_k,b_a_p)
		self.cx =  ccxt.binance({'apiKey':b_a_k,'secret':b_a_p,'enableRateLimit':True})

	def get_mon_balance(self,handler):
		resp =  handler.send('getbalance',account_index=mon_receiver_index)
		return resp['result']['balance']
	

	def get_balances(self,coin):
		returned_dcit = {}
		for x in self.coins_list:
			if x == coin:
				continue
			else:
				h = get_handler(x)
				if x == 'ETH':
					balance =float(Web3.fromWei(h.eth.getBalance(eth_test_provider_ad),'ether'))
					returned_dcit[x] = balance
				elif  x == 'XMR':
					balance  = self.get_mon_balance(h)
					returned_dcit[x] = balance
				else:
					balance = h.send('getbalance')
					returned_dcit[x] = balance
		return returned_dcit

	
	def get_exchanges_rates_for_amount(self,coin,amount):
		h = Handler()
		res_dict = {}
		for x in self.coins_list:
			if x == coin:
				continue
			else:
				if x == 'ETH':
					rate =  h.get_exchange_rate(coin,'ETH',1,amount)
					res_dict[x] = rate
				elif x == 'BTC':
					rate =  h.get_exchange_rate(coin,'BCH',1,amount)
					res_dict[x] = rate
				elif x == 'BCH':
					rate =  h.get_exchange_rate(coin,'BCH',1,amount)
					res_dict[x] = rate
				elif x == 'LTC':
					rate =  h.get_exchange_rate(coin,'LTC',1,amount)
					res_dict[x] = rate
				elif x == 'XMR':
					rate =  h.get_exchange_rate(coin,'XMR',1,amount)
					res_dict[x] = rate

		return res_dict

	
	def get_differences(self,balances,rates,coin):
		res_dict = {}
		for x in self.coins_list:
			if x == coin:
				continue
			else:
				rate = balances[x] - rates[x]
				if rate <= 0:
					continue
				else:
					res_dict[x] = rate

		return res_dict

	def get_real_diff(self,diff):
		h = Handler()
		res = {}
		for x in diff.items():
			price = h.get_single(x[0],x[-1])
			res[x[0]] = price
		return res




	# ethereum

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

	def check_balance(self,balance):
		if balance == 0:
			return True
		else:
			return False

	def get_eth_confirmation(self,hsh):
		return self.w.eth.getBlock('latest').number -  self.w.eth.getTransaction(hsh).blockNumber




	#

	#  Monero
	def get_mon_balance(self,handler):
		resp =  handler.send('getbalance',account_index=mon_receiver_index)
		return resp['result']['balance']


	def get_address_indice(self,address,handler):
		resp = handler.send('get_address_index',address=address)
		return resp['result']['index']['minor']
	def get_mon_received(self,address,handler):
		indice  = self.get_address_indice(address,handler)
		resp_dict = handler.send('getbalance',account_index=mon_receiver_index,address_indices=[indice])
		res = resp_dict['result']
		addresses =  res['per_subaddress']
		for addr in addresses:
			if address == addr['address']:
				balance = addr['balance']
				return balance

	def get_mon_txid(self,address,handler):
		resp  = handler.send('get_transfers',account_index=mon_receiver_index,in_=True)
		in_list =  resp['result']['in']
		for l in in_list:
			if l['address']  == address:
				return [l['txid'],l['amount']]

	def get_mon_confirmation(self,txid,handler):
		resp = handler.send('get_transfer_by_txid',txid=txid,account_index=mon_receiver_index)
		return resp['result']['transfer']['confirmations']


	#

	# other coins
	def get_transaction(self,address,trs):
		for tr in trs:
			if tr['address'] == address:
				return tr['txid']
			else:
				pass
		
		return False

	def get_confirmations(self,txid,handler):
		tr = handler.send('gettransaction',txid)
		return tr['confirmations']

	#

	def reconciliate(out_c,in_c,withdraw_address,amount):
		
					


	def get_new_balance(self,amount,out_address,in_address,out_c,in_c):
		try:
			handler1 = get_handler(out_c)
			if out_c == 'ETH':
				old_d = self.c.get_asset_balance(asset='ETH')['free']
				amount_out  = Web3.toWei(amount,'ether')
				print('sending the amount to ' + out_address)
				signed_txn = self.create_eth_transaction_cus(out_address,amount_out,eth_test_provider_p,handler1,eth_test_provider_ad)
				handler1.eth.sendRawTransaction(signed_txn.rawTransaction)
				print('transaction sent')
			elif out_c == 'XMR':
				old_d = self.c.get_asset_balance(asset='XMR')['free']
				print('sending')
				amount_out = round(amount,9)
				amount_out = int(amount_out * (10**12))
				print('sending amount : ',end=' ')
				print(amount_out)
				res = handler1.send('transfer',destinations=[{'amount':amount_out,'address':out_address}],account_index = mon_receiver_index)
				print(res)
			else:
				if out_c == 'BTC':
					old_d = self.c.get_asset_balance(asset='BTC')['free']
				elif out_c == 'BCH':
					old_d = self.c.get_asset_balance(asset='BCHABC')['free']
				elif out_c == 'LTC':
					old_d = self.c.get_asset_balance(asset='LTC')['free']
				print('sending')
				amount_out = round(amount,8)
				print('sending amount : ',end=' ')
				print(amount_out)
				res = handler1.send('sendtoaddress',out_address,amount_out)
				if not res:
					print('failed')

			print('checking if deposit arrived')
			restart = True
			while restart:
				if out_c == 'ETH':
					new_d = self.c.get_asset_balance(asset='ETH')['free']
				elif out_c == 'XMR':
					new_d = self.c.get_asset_balance(asset='XMR')['free']
				else:
					if out_c == 'BTC':
						new_d = self.c.get_asset_balance(asset='BTC')['free']
					elif out_c == 'BCH':
						new_d = self.c.get_asset_balance(asset='BCHABC')['free']
					elif out_c == 'LTC':
						new_d = self.c.get_asset_balance(asset='LTC')['free']

				if  new_d !=  old_d:
					restart = False
				else:
					continue
			

			




			print('withdrawing')


			input('waiting fro withdraw')

			print('now waiting for the withdraw')
			handler2 = get_handler(in_c)
			if in_c == 'ETH':
				print('start checking')
				print(in_address)
				while self.check_balance(handler2.eth.getBalance(in_address)):
					pass
				print('balance changed')
				print('getting block hash')
				res = get_address_transactions(in_address,handler2)
				confirmation = res[-1]
				while confirmation <  min_confirmation:
					confirmation = self.get_eth_confirmation(res[0])
					#print(confirmation)
				print('transaction  confirmed')
			elif in_c == 'XMR':
				print('start check')
				print(in_address)
				while self.check_balance(self.get_mon_received(in_address,handler2)):
					pass
				print('balance changed')
				print('getting txid')
				txid_resp = self.get_mon_txid(in_address,handler2)
				amount_in  = txid_resp[-1]/(10**12)
				txid = txid_resp[0]
				
				while self.get_mon_confirmation(txid,handler2) < min_confirmation:
					pass
				print('transaction confirmed')
			else:
				print('start check')
				print(in_address)
				while self.check_balance(handler2.send('getreceivedbyaddress',in_address)):
					pass
				print('balance changed')
				print('getting txid')
				txid = self.get_transaction(in_address,handler2.send('listtransactions',main_test_label))
				
				while self.get_confirmations(txid,handler2) < min_confirmation:
					pass
				print('transaction confirmed')
			return True
		except  Exception as e:
			print(str(e))
			return False


			







	def handle_pending(self,t):
		try:
			print('starting reconciliation task for transaction ID : ',end=' ')
			print(t.transaction_id)
			print('getting the transaction')
			tr = Transaction.objects.filter(transaction_id = t.transaction_id)[0]
			balances = self.get_balances(tr.out_currency)
			rates = self.get_exchanges_rates_for_amount(tr.out_currency,tr.amount_out)
			pre_differences = self.get_differences(balances,rates,tr.out_currency)
			differences  = self.get_real_diff(pre_differences)
			sorted_diff =  sorted(differences.items(), key=lambda kv: kv[1])
			print(sorted_diff)
			print('the best paire is')
			print(sorted_diff[-1])
			s_addr = input('sending address ==> ')
			in_c = tr.out_currency
			handler = get_handler(in_c)

			if in_c == 'ETH':
				account = handler.eth.account.create('check this')
				print(account.privateKey)
				address = account.address
			elif in_c == 'XMR':
				resp = handler.send('create_address',account_index=mon_receiver_index)
				address = resp['result']['address']
			else:
				address = handler.send('getnewaddress',main_test_label)

			print('start the sub_worker')
			amnt = rates[sorted_diff[-1][0]]  +  (rates[sorted_diff[-1][0]] * 5/100)
			res = self.get_new_balance(amnt,s_addr,address,sorted_diff[-1][0],in_c,tr.amount_out,rates[sorted_diff[-1][0]])
			if res:
				input('success')
			else:
				input('failed')

			

			






		except Exception as e:
			input(str(e))

	

	def run(self):
		while True:
			t_pending = Task.objects.filter(status='pending')
			for t in t_pending:
				res = self.handle_pending(t)
			input('check')
				
