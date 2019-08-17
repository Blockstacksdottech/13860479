from django.shortcuts import render,redirect,HttpResponseRedirect,HttpResponse
from exchanger.settings import  *
from .models import *
import requests as req
import json
import random

# Create your views here.


def get_exchange_rates():
	resp = req.get("https://api.nomics.com/v1/currencies/ticker?key="+api_key+'&ids=BTC,BCH,ETH,XMR,LTC&interval=1h&convert=USD')
	data = json.loads(resp.content.decode())
	ret_dict  = {}
	for x in data:
		ret_dict[x['currency']] = str(round(float(x['price']),2))
	return ret_dict

def index(request):
	ret_dict = get_exchange_rates()
	return render(request,'index.html',ret_dict)

# exchange section

def exchange_pannel(request):
	curr_in = request.GET.get('in','')
	curr_out = request.GET.get('out','')
	
	if curr_in != '' and curr_out != '':
		resp = {
			'cur_in' : curr_in,
			'cur_out' : curr_out,
			'api_link' : api_link

		}
		ret_dict = get_exchange_rates()
		resp.update(ret_dict)
		return render(request,'exchange_filled.html',resp)
		
	else:
		print('here')
		return redirect('/')

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
		out_mod = Currencies.objects.filter(currency=in_c)[0]
		in_mod = Currencies.objects.filter(currency=out_c)[0]
		# when the nodes are integrated generate an address directly from the client
		t = Transaction.objects.create(
			transaction_id = idd,
			return_address = return_address,
			refund_address = refund_address,
			recv_address = in_mod.test_address,
			in_currency = in_c,
			out_currency = out_c,
			hash_tr = 'None'
			
		)
		t.save()

		
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
				'c' : t.out_currency,
				'amount': t.amount_out,
				'hash':t.hash_tr

		}
		return render(request,'transaction_done.html',ret_dict)
	else:
		ret_dict ={
			'id':t.transaction_id,
			'in_c':t.in_currency,
			'ref_add':t.refund_address,
			'out_c':t.out_currency,
			'rec_add':t.return_address,
			'sys_add':t.recv_address,
			'date':t.created,
			'message':task.action,

		}
		return render(request,'transaction_hold.html',ret_dict)




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