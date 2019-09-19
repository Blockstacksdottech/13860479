from binance.client import Client
from .settings import *


class Handler:
	def __init__(self):
		self.client = Client(b_a_k,b_a_p)

	
	def get_exchange_rate(self,in_c,out_c,fee,received):
		amount  = received
		if in_c == 'BCH':
			in_c  = 'BCHABC'
		if out_c == 'BCH':
			out_c =   'BCHABC'
		first_c = self.client.get_ticker(symbol='{0}USDT'.format(str(in_c)))
		second_c = self.client.get_ticker(symbol='{0}USDT'.format(str(out_c)))
		rate = float(first_c['lastPrice']) / float(second_c['lastPrice'])
		out_value = rate * (amount - (amount * (fee/100)))
		#out_value = rate * (amount)
		return out_value

	def get_single(self,coin,amount):
		print(coin)
		if coin == 'BCH':
			coin = 'BCHABC'
		tick = self.client.get_ticker(symbol='{0}USDT'.format(str(coin)))
		price = float(tick['lastPrice'])

		return price
	
	def get_rate(self,coin,amount):
		if coin == 'BCH':
			coin = 'BCHABC'
		
		tick = self.client.get_ticker(symbol='{0}USDT'.format(str(coin)))
		price = float(tick['lastPrice'])
		price = round(amount / price,8)
		return price
