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
					prec = h.get_precision('ETH')
					rate =  round(h.get_exchange_rate(coin,'ETH',1,amount),prec) + (10**-prec)
					res_dict[x] = rate
				elif x == 'BTC':
					prec = 3
					rate =  round(h.get_exchange_rate(coin,'BTC',1,amount),prec) + (10**-prec)
					res_dict[x] = rate
				elif x == 'BCH':
					prec = h.get_precision('BCH')
					rate =  round(h.get_exchange_rate(coin,'BCH',1,amount),prec) + (10**-prec)
					res_dict[x] = rate
				elif x == 'LTC':
					prec = h.get_precision('LTC')
					rate =  round(h.get_exchange_rate(coin,'LTC',1,amount),prec) + (10**-prec)
					res_dict[x] = rate
				elif x == 'XMR':
					prec = h.get_precision('XMR')
					rate =  round(h.get_exchange_rate(coin,'XMR',1,amount),prec) + (10**-prec)
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

	def reconciliate(self,out_c,in_c,withdraw_address,amount_in):
		h = Handler()
		if out_c == 'BCH':
			out_c = 'BCHABC'
		if in_c == 'BCH':
			in_c = 'BCHABC'
		if in_c == 'BTC':
			pass
		else:
			#prec  = 3
			#first_rate = round(h.get_exchange_rate_rec(in_c,'BTC',3,amount_in),prec) + (10**-prec)

			#print(first_rate)
			#second_rate = round(h.get_exchange_rate_rec('BTC',out_c,3,first_rate),prec) + (10**-prec)
			#print(second_rate)
			input('check')
			if out_c == 'BCH':
				out_c_b = 'BCHABC'
			else:
				out_c_b  = out_c
			
			if in_c == 'BCH':
				in_c_b = 'BCHABC'
			else:
				in_c_b = in_c
			old_btc_balance = self.client.get_asset_balance(asset='BTC')['free']
			precision = h.get_precision(in_c_b)
			old_in_balance  = round(self.client.get_asset_balance(asset=in_c_b)['free'],precision)
			trade_1 = self.c.order_market_buy(symbol='{0}BTC'.format(in_c_b),quantity=round(h.get_exchange_rate(in_c_b,'BTC',0,old_in_balance),3))
			print(trade_1)
			print('checking for trade')
			out_c = 'BTC'
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

				if  new_d !=  old_btc_balance:
					restart = False
				else:
					continue
			new_btc_balance = self.c.get_asset_balance(asset='BTC')['free']
			old_out_balance = self.c.get_asset_balance(asset=out_c_b)['free']
			trade2 = self.c.order_market_sell(symbol='{0}BTC'.format(out_c_b),quantity=round(h.get_exchange_rate('BTC',out_c_b,0,new_btc_balance),3))
			print(trade2)
			print('checking for trade')
			out_c = out_c_b
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

				if  new_d !=  old_out_balance:
					restart = False
				else:
					continue
			final_balance = self.c.get_asset_balance(asset=out_c_b)['free']
			precision = h.get_precision(out_c_b)
			with_res = self.c.withdraw(asset=out_c_b,address=withdraw_address,amount=round(final_balance,precision))
			try:
				if with_res['message'] == 'success':
					return True
				else:
					print('failed withdraw')
					return False
			except Exception as e:
				print(str(e))
				print('failed withdraw')
				return False

			

			





			
		


		
					


	def get_new_balance(self,amount,out_address,in_address,out_c,in_c,transaction_amount): # transaction_amount is the amount needed to receive back
		try:
			handler1 = get_handler(out_c)
			if out_c == 'ETH':
				old_d = self.c.get_asset_balance(asset='ETH')['free']
				amount_out  = Web3.toWei(amount,'ether')
				amount +=  float(Web3.fromWei(handler1.eth.gasPrice * 100000,'ether'))
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
				print('here in btc')
				"""
				if out_c == 'BTC':
					old_d = self.c.get_asset_balance(asset='BTC')['free']
				elif out_c == 'BCH':
					old_d = self.c.get_asset_balance(asset='BCHABC')['free']
				elif out_c == 'LTC':
					old_d = self.c.get_asset_balance(asset='LTC')['free']

				"""
				print('sending')
				amount_out = round(amount,8)
				print('sending amount : ',end=' ')
				print(amount_out)
				res = handler1.send('sendtoaddress',out_address,amount_out)
				if not res:
					print('failed')

			print('checking if deposit arrived')
			restart = False
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
			self.reconciliate(out_c,in_c,in_address,transaction_amount)


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
			print('something went wrong')
			return False


			







	def handle_pending(self,t):
		try:
			print('starting reconciliation task for transaction ID : ',end=' ')
			print(t.transaction_id)
			print('getting the transaction')
			hb = Handler()
			tr = Transaction.objects.filter(transaction_id = t.transaction_id)[0]
			####
			prec = 3
			first_rate = round(hb.get_exchange_rate_rec(tr.out_currency,'BTC',3,tr.amount_out),prec) + (10**-prec)
			second_rate = round(hb.get_exchange_rate_rec('BTC',tr.out_currency,3,first_rate),prec) + (10**-prec)


			#####
			
			
			balances = self.get_balances(tr.out_currency)
			input(tr.amount_out)
			#r_amount = float(tr.amount_out) + (float(tr.amount_out * 5/100)) + hb.get_usd_equiv(tr.out_currency,10)
			r_amount = second_rate + hb.get_usd_equiv(tr.out_currency,10)
			print(second_rate)
			input(r_amount)
			r_amount_single  = hb.get_single(tr.out_currency,r_amount)
			print(r_amount_single)
			if round(100-r_amount_single,3) > 0:
				r_amount = hb.get_usd_equiv(tr.out_currency,100)
				
			else:
				pass
			input('check')

				
			
			rates = self.get_exchanges_rates_for_amount(tr.out_currency,r_amount)
			print('after rates')
			pre_differences = self.get_differences(balances,rates,tr.out_currency)
			print('after pre')
			differences  = self.get_real_diff(pre_differences)
			print('after diff')
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
			#if sorted_diff[-1][0] == 'BTC':
			#	prec = 3
			#else:
			#	prec = hb.get_precision(sorted_diff[-1][0])
			amnt = rates[sorted_diff[-1][0]]  
			print(sorted_diff[-1][0])
			input(amnt)
			res = self.get_new_balance(amnt,s_addr,address,sorted_diff[-1][0],in_c,tr.amount_out)
			if res:
				input('success')
			else:
				input('failed')

			

			






		except Exception as e:
			input(str(e))


	def recheck_balance(self,transaction):
		self.handler2 = get_handler(transaction.out_currency)
		self.transaction  = transaction
		if 'ETH' == self.transaction.out_currency:
			balance =float(Web3.fromWei(self.handler2.eth.getBalance(eth_test_provider_ad),'ether'))
		elif 'BTC' == self.transaction.out_currency:
			balance = self.handler2.send('getbalance')
		elif 'LTC' == self.transaction.out_currency:
			balance = self.handler2.send('getbalance')
			
		elif 'XMR' == self.transaction.out_currency:
			balance = self.get_mon_balance(self.handler2)
		
		if self.transaction.amount_out >= balance:
			return False
		else:
			return True

	

	def run(self):
		while True:
			#t_pending = Task.objects.filter(status='pending')
			t_pending  = Task.objects.filter(transaction_id = '7353548484328')
			for t in t_pending:
				transaction = Transaction.objects.filter(transaction_id = t.transaction_id)
				print('here')
				print(transaction)
				if len(transaction) == 0:
					continue
				else:
					check_res = self.recheck_balance(transaction[0])
					if check_res:
						res = self.handle_pending(t)
					else:
						continue
			input('check')
				
