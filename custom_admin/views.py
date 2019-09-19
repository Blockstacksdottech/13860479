from django.shortcuts import render,HttpResponse,redirect
from .models import *

# Create your views here.



def view_login(request):
	return render(request,'new_login.html')

def verify_login(request):
	if request.method == 'POST':
		username = request.POST.get('username','')
		password = request.POST.get('password','')

		if username == '' or password == '':
			return render(request,'new_login.html',{'message':'empty field'})

		usr = User.objects.filter(username =  username )
		if len(usr) != 0:
			usr = usr[0]
			if password == usr.password:
				request.session['user'] = usr.username
				return  redirect('/pannel')
			else:
				return render(request,'new_login.html',{'message':'password is incorrect'})
				
		else:
			return render(request,'new_login.html',{'message':'user not found'})
		
	else:
		return HttpResponse('not valid')


def show_pannel(request):
	username = request.session.get('user','')
	if username != '':
		usr = User.objects.filter(username = username)[0]
		return render(request,'pannel.html',{'username':usr.username})
	else:
		return render(request,'new_login.html',{'message':'please new_login first'})


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


#ndhkjkuejmx