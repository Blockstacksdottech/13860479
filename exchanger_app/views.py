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
import mailchimp3
from django.core.mail import send_mail
from monero.address import address as mon_checker

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
		try:
			resp = req.get('https://coinmarketcap.com/')
		except:
			time.sleep(5)
			continue
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


def check_valid(coin,address):
	h = get_handler(coin)
	if coin == 'ETH':
		res = h.isAddress(address)
	elif coin == 'XMR':
		try:
			print('XMR')
			print(address)
			pre_res = mon_checker(address)
			res = True
		except:
			res = False
	else:
		if coin == 'LTC':
			resp = h.send('validateaddress',address)
			res = resp['isvalid']
		else:
			print('here')
			print(coin)
			res = h.send('validateaddress',address)['isvalid']
	return res




def validator(request):
	in_c = request.POST.get('inCurrency','')
	in_addr =  request.POST.get('refundAddress','')
	out_c = request.POST.get('outCurrency','')
	out_addr = request.POST.get('returnAddress','')
	if in_c != '' and out_c != '' and in_addr != '' and out_addr != '':
		in_status =  check_valid(in_c,in_addr)
		time.sleep(3)
		out_status = check_valid(out_c,out_addr)
		if in_status and out_status:
			return {
				'valid' : True
			}
		else:
			if in_status:
				return {
					'valid':False,
					'reason':2
				}
			elif out_status:
				return {
					'valid':False,
					'reason':1
				}
			else:
				return {
					'valid':False,
					'reason':0
				}










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
	

def get_equivalent(lst):
	h = Handler()
	final_amount = 0
	for x in lst:
		if x.out_currency == 'BTC':
			final_amount += x.amount_out
		else:
			final_amount += h.get_exchange_rate(x.out_currency,'BTC',1,x.amount_out)
	
	return round(final_amount,4)

	
def get_rates():
	tr1 = Transaction.objects.filter(out_currency = 'BTC')
	tr2 = Transaction.objects.filter(in_currency='BTC')
	trs = Transaction.objects.all() 
	lst = {'altToBTC':float(len(tr1)),'BtcToAlt':float(len(tr2)),'AltToAlt':float(len(trs) - len(tr1) - len(tr2))}
	lst_sorted = sorted(lst.items(), key=lambda kv: kv[1])
	return sorted(lst_sorted)[::-1]

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
	h_c_s = hacking_status.objects.all()[0]
	h_amount  = h_c_s.amount
	total = len(Transaction.objects.all())
	
	processed_cont = [Transaction.objects.filter(transaction_id = t.transaction_id)[0] for t in Task.objects.filter(status='done') if len(Transaction.objects.filter(transaction_id = t.transaction_id)) != 0]
	processed = len(processed_cont)
	equivalent = get_equivalent(processed_cont)
	rates = get_rates()
	ret_dict.update({'total':total,'processed':processed,'volume':str(equivalent),'hck':str(h_amount),
	rates[0][0]:rates[0][1],
	rates[1][0]:rates[1][1],
	rates[2][0]:rates[2][1]
	
	})

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
			'c_in'  : curr_in.lower(),
			'c_out' : curr_out.lower(),
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
		check_res = validator(request)
		if check_res['valid']:
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
				check_res = {
			'valid': False,
			'reason':4
		}
				return HttpResponse(json.dumps(check_res))

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
				'valid':True,
				'processId':t.transaction_id
			}))

		else:
			return HttpResponse(json.dumps(check_res))




	else:
		check_res = {
			'valid': False,
			'reason':4
		}
		return HttpResponse(json.dumps(check_res))

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

	ret_dict2 = get_exchange_rates()
	ret_dict.update(ret_dict2)
	return render(request,'exchange_details.html',ret_dict)

def check(request,idd):
	t = Transaction.objects.filter(transaction_id = idd)
	if len(t) == 0:
		return render(request,'404.html',{'msg':'Transaction not found'})
	else:
		t = t[0]

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
		ret_dict2 = get_exchange_rates()
		ret_dict.update(ret_dict2)
		return render(request,'transaction_done.html',ret_dict)
	elif 'Awaiting deposit ...'  in task.status:
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
		ret_dict2 = get_exchange_rates()
		ret_dict.update(ret_dict2)
		return render(request,'exchange_details.html',ret_dict)
	else:
		ret_dict ={
			'currency':t.out_currency,
			'address':t.return_address,
			'amount':t.amount_out
			

		}
		ret_dict2 = get_exchange_rates()
		ret_dict.update(ret_dict2)
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

def send_mail_contact(request):
	name = request.GET.get('name','')
	mail = request.GET.get('email','')
	content = request.GET.get('content','')
	if name != '' and mail != '' and content != '':
		send_mail(
    '[Morphex] Contact email [{0}]'.format(name),
    content,
    mail,
    ['sky.red2212@gmail.com'],
    fail_silently=False,
)		
		return render(request,'success.html')
	else:
		return redirect('/contact')

def subscribe(request):
	
	mail = request.GET.get('email','')
	if mail != '':
		a = mailchimp3.MailChimp(mail_api_key)
		ret_dict = get_exchange_rates()
		ret_dict.update({
			'message':'subscribed to the newsletter'
			})
		a.lists.members.create(mail_list_id,{'email_address':mail,'status':'subscribed'})
		print('error here')
		s = subscribers.objects.create(email=mail)
		s.save()

		return render(request,'success.html',ret_dict)
		#return redirect('/')
	else:
		return redirect('/')

def faq(request):
	ret_dict = get_exchange_rates()
	return render(request,'faq.html',ret_dict)




