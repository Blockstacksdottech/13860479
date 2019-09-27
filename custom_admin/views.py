from django.shortcuts import render,HttpResponse,redirect
from exchanger_app.binance_handler import *
from exchanger_app.nodes_handler  import *
from exchanger_app.models import *
from exchanger.settings import *
from web3 import Web3
from .models import *
import os

# Create your views here.


def view_terms(request):
	
	return render(request,'terms.html')

def view_login(request):
	username = request.session.get('user','')
	if username != '':
		return redirect('/panel')
	else:

		return render(request,'blog_login.html')

def verify_login(request):
	if request.method == 'POST':
		username = request.POST.get('username','')
		password = request.POST.get('password','')

		if username == '' or password == '':
			return render(request,'blog_login.html',{'message':'empty field'})

		usr = User.objects.filter(username =  username )
		if len(usr) != 0:
			usr = usr[0]
			if password == usr.password:
				request.session.set_expiry(0)
				request.session['user'] = usr.username
				return  redirect('/panel')
			else:
				return render(request,'blog_login.html',{'message':'password is incorrect'})
				
		else:
			return render(request,'blog_login.html',{'message':'user not found'})
		
	else:
		return HttpResponse('not valid')
def get_mon_balance(handler):
	resp =  handler.send('getbalance',account_index=mon_receiver_index)
	return resp['result']['balance']

def get_balances(amount,dct):
	coins = ['BTC','BCH','ETH','LTC','XMR']
	b = Handler()

	for x in coins:
		h = get_handler(x)
		


		if 'ETH' == x:
			balance =float(Web3.fromWei(h.eth.getBalance(eth_test_provider_ad),'ether'))
			max_val = b.get_rate(x,amount)

			
			moyen = round((balance/max_val)  * 100,2)
			balance  = round(balance,4)
			max_val = round(max_val,4)

			dct[x]  = [balance,max_val,moyen]
		elif 'BTC' == x:
			balance = h.send('getbalance')
			max_val = b.get_rate(x,amount)
			
			moyen = round((balance/max_val)  * 100,2)
			balance  = round(balance,4)
			max_val = round(max_val,4)
			dct[x]  = [balance,max_val,moyen]
		elif 'LTC' == x:
			balance = h.send('getbalance')
			max_val = b.get_rate(x,amount)
			moyen = round((balance/max_val)  * 100,2)
			balance  = round(balance,4)
			max_val = round(max_val,4)
			dct[x]  = [balance,max_val,moyen]
		elif 'BCH' == x:
			balance = h.send('getbalance')
			max_val = b.get_rate(x,amount)
			moyen = round((balance/max_val)  * 100,2)
			balance  = round(balance,4)
			max_val = round(max_val,4)
			dct[x]  = [balance,max_val,moyen]
		elif 'XMR' == x:
			balance = round((get_mon_balance(h) / 10**12),2)
			max_val = b.get_rate(x,amount)
			moyen = round((balance/max_val)  * 100,2)
			balance  = round(balance,4)
			max_val = round(max_val,4)
			dct[x]  = [balance,max_val,moyen]
	return dct

def get_top_list():
	d_trs = Task.objects.filter(status='done')
	b = Handler()
	temp_dct =  {}
	for x in d_trs:
		tr = Transaction.objects.filter(transaction_id=x.transaction_id)
		if len(tr) == 0:
			continue
		else:
			tr = tr[0]
		rate = b.get_inverse(tr.in_currency,tr.amount_in)
		temp_dct[tr.transaction_id] = [rate,tr]
	
	ordered_paires = sorted(temp_dct.items(), key=lambda kv: kv[1][0])[::-1]
	print(ordered_paires)
	return ordered_paires


def show_pannel(request):
	username = request.session.get('user','')
	if username != '':
		usr = User.objects.filter(username = username)[0]
		
		sett = Settings.objects.all()[0]
		trs = Transaction.objects.all()
		w_taks = Task.objects.filter(status='waiting')
		e_tasks = Task.objects.filter(status='exchanging')
		ret_dict = {
			'username':usr.username,
			't_count':str(len(trs)),
			'p_count':str(len(w_taks)),
			'e_count':str(len(e_tasks)),


			
			
			
			}
		ret_dict = get_balances(sett.max_amount,ret_dict)
		top_list =  get_top_list()
		print('here')
		ret_dict['top'] = top_list
		l_trs = Transaction.objects.all().order_by('-created')[:10]
		ret_dict['last'] = l_trs
		return render(request,'panel.html',ret_dict)
	else:
		return render(request,'blog_login.html',{'message':'please blog_login first'})


def log_out(request):
	del request.session['user']
	return redirect('/custadmin')

def get_details(request):
	pass

def change_min(request):
	if request.method == 'POST':
		min_val = request.POST.get('min','')
		if min_val != '':
			s = Settings.objects.all()[0]
			s.min_amount = min_val
			s.save()
			return redirect('/settings')
		else:
			return redirect('/settings')
	else:
		return redirect('/settings')

def change_max(request):
	if request.method == 'POST':
		min_val = request.POST.get('max','')
		if min_val != '':
			s = Settings.objects.all()[0]
			s.max_amount = min_val
			s.save()
			return redirect('/settings')
		else:
			return redirect('/settings')
	else:
		return redirect('/settings')

def change_delay(request):
	if request.method == 'POST':
		min_val = request.POST.get('delay','')
		if min_val != '':
			s = Settings.objects.all()[0]
			s.delay = min_val
			s.save()
			return redirect('/settings')
		else:
			return redirect('/settings')
	else:
		return redirect('/settings')

def change_fee(request):
	if request.method == 'POST':
		min_val = request.POST.get('fee','')
		if min_val != '':
			s = Settings.objects.all()[0]
			s.service_fee = min_val
			s.save()
			return redirect('/settings')
		else:
			return redirect('/settings')
	else:
		return redirect('/settings')

def change_stat(request):
	if request.method == 'POST':
		min_val = request.POST.get('activated','')
		if min_val != '':
			s = Settings.objects.all()[0]
			if min_val == '1':
				s.activated = True
			else:
				s.activated = False
			s.save()
			return redirect('/settings')
		else:
			return redirect('/settings')
	else:
		return redirect('/settings')

def change_coin_status(request):
	coins = ['BTC','ETH','BCH','LTC','XMR']
	if request.method == 'POST':
		for  x in coins:
			min_val = request.POST.get(x,'')
			if min_val != '':
				sett  = Settings.objects.all()[0]
				s = sett.currencies_s_set.filter(currency = x)[0]
				if min_val == '1':
					s.activated = True
				else:
					s.activated = False
				s.save()
		
		return redirect('/settings')
		
	else:
		return redirect('/settings')

def remove_tr(request,idd):
	username = request.session.get('user','')
	if username != '':
		tr = Transaction.objects.filter(transaction_id = idd)
		if len(tr) == 0:
			return redirect('/custadmin')
		else:
			tr  = tr[0]
			tr.delete()
			return redirect('/custadmin')
	else:
		return render(request,'blog_login.html',{'message':'please blog_login first'})

	


#ndhkjkuejmx