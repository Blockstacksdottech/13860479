from django.shortcuts import render,redirect,HttpResponseRedirect,HttpResponse
from exchanger.settings import  *
from .models import *
from custom_admin.models import *
import requests as req
import json
import random
import threading
import time
from bs4 import BeautifulSoup
from .nodes_handler import *
from .in_listener import *

# Create your views here.

"""
def get_exchange_rates_api():
	while True:
		resp = req.get("https://api.nomics.com/v1/currencies/ticker?key="+api_key+'&ids=BTC,BCH,ETH,XMR,LTC&interval=1h&convert=USD')
		data = json.loads(resp.content.decode())
		
		for x in data:
			#print(x)
			filt =  Prices.objects.filter(currency=x['currency'])
			if len(filt) != 0 :
				filt[0].price = round(float(x['price']),2)
				filt[0].save()
			else:
				f = Prices.objects.create(currency=x['currency'],price=round(float(x['price']),2))
				f.save()
		time.sleep(10*60)
"""

def get_exchange_rates_api():
	while True:
		resp = req.get('https://coinmarketcap.com/')
		soup = BeautifulSoup(resp.content.decode(),'html.parser')
		table = soup.find('table')
		trs = table.find('tbody').findAll('tr')
		for tr in trs:
			#print('exchanger')
			tds = tr.findAll('td')
			#print(tds[1]['data-sort']  + ' ==> ' + str(round(float(tds[3]['data-sort']),2)) )
			filled = False
			if 'id-bitcoin' == tr['id']:
				key = 'BTC'
				value = round(float(tds[3]['data-sort']),2)
				filled = True
			elif 'bitcoin-cash' in tr['id']:
				key = 'BCH'
				value = round(float(tds[3]['data-sort']),2)
				filled = True
			elif 'id-ethereum' == tr['id']:
				key = 'ETH'
				value = round(float(tds[3]['data-sort']),2)
				print('eth')
				print(tds[3]['data-sort'])
				filled = True
			elif 'litecoin' in tr['id']:
				key = 'LTC'
				value = round(float(tds[3]['data-sort']),2)
				print(tds[3]['data-sort'])
				filled = True
			elif 'monero' in tr['id']:
				key = 'XMR'
				value = round(float(tds[3]['data-sort']),2)
				print(tds[3]['data-sort'])
				filled = True
			
			if filled:
				#print('changement')
				filt =  Prices.objects.filter(currency=key)
				if len(filt) != 0 :
					#print('updating')
					filt[0].price = value
					filt[0].save()
				else:
					f = Prices.objects.create(currency=key,price=value)
					f.save()
			else:
				pass
		time.sleep(20)












def start_updater_internally():
	t = threading.Thread(target=get_exchange_rates_api)
	t.daemon = True
	t.start()
	print('started')

def start_updater(requests):
	start_updater_internally()
	return HttpResponse('success')


def get_exchange_rates():
	counter = 0
	while counter <= 10:
		currencies = Prices.objects.all()
		if len(currencies) >= 5:
			ret_dict  = {}
			for curr in currencies:
				ret_dict[curr.currency] =  curr.price
			return ret_dict
		else:
			time.sleep(1)
			counter += 1
			continue
	

	


def index(request):
	listnr = Listener.objects.filter(name='price_updater')
	if len(listnr) != 0 and listnr[0].status:
		pass
	else:
		if len(listnr) != 0:
			start_updater_internally()
			listnr[0].status = True
			listnr[0].save()
		
		else:
			start_updater_internally()
			lstnr = Listener.objects.create(name='price_updater',status=True)
			lstnr.save()

	ret_dict = get_exchange_rates()
	return render(request,'index.html',ret_dict)

# exchange section

def exchange_pannel(request):
	curr_in = request.GET.get('in','')
	curr_out = request.GET.get('out','')
	
	if curr_in != '' and curr_out != '':
		b_h = Handler()
		s = Settings.objects.all()[0]
		min1 = b_h.get_rate(curr_in,s.min_amount)
		min2 = b_h.get_rate(curr_out,s.min_amount)
		resp = {
			'cur_in' : curr_in,
			'cur_out' : curr_out,
			'api_link' : api_link,
			'min1':min1,
			'min2':min2

		}
		ret_dict = get_exchange_rates()
		resp.update(ret_dict)
		return render(request,'exchange_filled.html',resp)
		
	else:
		print('here')
		return redirect('/')


def run_lstn(coin,t,l):

	if coin == 'ETH':
		account = l
		lstnr = listener(t.in_currency,account.privateKey,t.transaction_id)
	

	else:
		address = l
		lstnr = listener(t.in_currency,address,t.transaction_id)
	
	lstnr.start_c(coin)

	


def start(request):
	if request.method == "POST":
		in_c  = request.POST.get('inCurrency','')
		out_c = request.POST.get('outCurrency','')
		refund_address = request.POST.get('refundAddress','')
		return_address = request.POST.get('returnAddress','')
		while True:
			idd = str(random.randrange(10000,10000000000000))
			if len(Transaction.objects.filter(transaction_id = idd)) != 0:
				continue
			else:
				break
		#out_mod = Currencies.objects.filter(currency=out_c)[0]
		#in_mod = Currencies.objects.filter(currency=in_c)[0]
		handler = get_handler(in_c)
		if handler:
			pass
		else:
			return HttpResponse(json.dumps({
			'processId':'undefined'
		}))

		# get new address
		if in_c == 'ETH':
			account = handler.eth.account.create('check this')
			address = account.address
		elif in_c == 'XMR':
			resp = handler.send('create_address',account_index=mon_receiver_index)
			address = resp['result']['address']
		else:
			address = handler.send('getnewaddress',main_test_label)
		
		






		# when the nodes are integrated generate an address directly from the client
		t = Transaction.objects.create(
			transaction_id = idd,
			return_address = return_address,
			refund_address = refund_address,
			recv_address = address, #make an address getter
			in_currency = in_c,
			out_currency = out_c,
			hash_tr = 'None'
			
		)
		t.save()
		
		if in_c == 'ETH':
			this_arg  = account
		else:
			this_arg = address
		tr = threading.Thread(target=run_lstn,args=(in_c,t,this_arg,))
		tr.daemon = True
		tr.start()

		
		return HttpResponse(json.dumps({
			'processId':t.transaction_id
		}))




	else:
		return HttpResponse(json.dumps({
			'processId':'undefined'
		}))

def view_tr(request,idd):
	pass
	t = Transaction.objects.filter(transaction_id = idd)[0]
	ret_dict = {
			'id':t.transaction_id,
			'incomeCurrency':t.in_currency,
			'outCurrency':t.out_currency,
			'systemeAddress':t.recv_address,
			'time':t.created,
			'recvAddress':t.return_address,
			'returnAddress':t.refund_address
		}
	return render(request,'exchange_details.html',ret_dict)

def check(request,idd):
	t = Transaction.objects.filter(transaction_id = idd)[0]
	task = Task.objects.filter(transaction_id = t.transaction_id)[0]
	if 'done' in task.status:
		ret_dict = {
				'addr':t.return_address,
				'c_in':t.in_currency,
				'in':t.amount_in,
				'c_out' : t.out_currency,
				'out': t.amount_out,
				'hash':t.hash_tr

		}
		return render(request,'transaction_done.html',ret_dict)
	elif 'waiting'  in task.status:
		ret_dict ={
			'id':t.transaction_id,
			'in_c':t.in_currency,
			'ref_add':t.refund_address,
			'out_c':t.out_currency,
			'rec_add':t.return_address,
			'sys_add':t.recv_address,
			'date':t.created,
			'message':task.action,
			'status':task.status

		}
		return render(request,'exchange_details.html',ret_dict)
	else:
		ret_dict ={
			'currency':t.out_currency,
			'address':t.return_address,
			'amount':t.amount_out
			

		}
		return render(request,'exchanging.html',ret_dict)




####


def howitworks(request):
	ret_dict = get_exchange_rates()
	return render(request,'how_it_works.html',ret_dict)	

def checkup(request):
	ret_dict = get_exchange_rates()
	return render(request,'checkup.html',ret_dict)

def contact(request):
	ret_dict = get_exchange_rates()
	return render(request,'contact.html',ret_dict)

def subscribe(request):
	
	mail = request.GET.get('email','')
	if mail != '':
		ret_dict = get_exchange_rates()
		ret_dict.update({
			'message':'subscribed to the newsletter'
			})
		return render(request,'success.html',ret_dict)
	else:
		return redirect('/')

def faq(request):
	ret_dict = get_exchange_rates()
	return render(request,'faq.html',ret_dict)




