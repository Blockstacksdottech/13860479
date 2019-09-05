from web3 import Web3,HTTPProvider
import requests as req
import json
from .settings import *
from requests.auth import HTTPDigestAuth


#needed variable

headers = {'content-type': 'application/json'}
payload = {"jsonrpc": "1.0", "id":"curltest", "method": "", "params": [] }
payload_2 = {"jsonrpc":"2.0","id":"0","method":"","params":{}}



class Bitcoin:
	def __init__(self):
		self.user = bitcoin_user
		self.password = bitcoin_password
		self.url = 'http://{0}:{1}@23.254.176.26:18332/'.format(self.user,self.password)

	
	def send(self,command,*args):
		if len(args) != 0:
			params = [x for x in args]
		else:
			params = []
		
		custom_payload = payload.copy()
		custom_payload['method'] = command
		custom_payload['params'] = params

		# sending and recieving response from the node

		resp = req.post(self.url,json = custom_payload,headers = headers)
		data = json.loads(resp.content.decode())
		if data['error']:
			return False
		else:
			return data['result']
class Monero:
	def __init__(self):
		self.user  = monero_user
		self.password = monero_password
		self.url = 'http://127.0.0.1:18083/json_rpc'.format(self.user,self.password)
	def send(self,command,**kwargs):
		params = dict(kwargs)
		print(params)
		custom_payload = payload_2.copy()
		custom_payload['method'] = command
		custom_payload['params'] = params
		print(custom_payload)

		resp = req.post(self.url ,auth=HTTPDigestAuth(self.user,self.password), json=custom_payload,headers=headers)
		print(resp.content.decode())
		data = json.loads(resp.content.decode())
		print(data)
		if 'error' in data.keys():
			print(data['error'])
			return False

		return data


class BitcoinCash:
	def __init__(self):
		self.user = bitcoin_cash_user
		self.password = bitcoin_cash_password
		self.url = 'http://{0}:{1}@23.254.176.26:8355/'.format(self.user,self.password)

	
	def send(self,command,*args):
		if len(args) != 0:
			params = [x for x in args]
		else:
			params = []
		
		custom_payload = payload.copy()
		custom_payload['method'] = command
		custom_payload['params'] = params

		# sending and recieving response from the node

		resp = req.post(self.url,json = custom_payload,headers = headers)
		data = json.loads(resp.content.decode())
		if data['error']:
			return False
		else:
			return data['result']

class Litecoin:
	def __init__(self):
		self.user = litecoin_user
		self.password = litecoin_password
		self.url = 'http://{0}:{1}@23.254.176.26:19332/'.format(self.user,self.password)

	
	def send(self,command,*args):
		if len(args) != 0:
			params = [x for x in args]
		else:
			params = []
		
		custom_payload = payload.copy()
		custom_payload['method'] = command
		custom_payload['params'] = params

		# sending and recieving response from the node

		resp = req.post(self.url,json = custom_payload,headers = headers)
		data = json.loads(resp.content.decode())
		print(data)
		if data['error']:
			return False
		else:
			return data['result']



def get_handler(coin):
	if coin == 'BTC':
		return Bitcoin()
	elif coin == 'BCH':
		return BitcoinCash()
	elif coin == 'LTC':
		return Litecoin()
	elif coin == 'XMR':
		return Monero()
	elif coin =='ETH':
		w = Web3(HTTPProvider('http://23.254.176.26:8546'))
		if w.isConnected():
			return w
		else:
			return False






	