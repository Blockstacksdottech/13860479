from django.shortcuts import render,HttpResponse,get_object_or_404
from .models import *
from exchanger_app.models import *


# Create your views here.

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

def view_blog(request):
	posts = Posts.objects.all()
	ret_dict = get_exchange_rates()
	ret_dict['posts']=posts
	return render(request,'blog_main.html',ret_dict)

def view_post(request,slug):
	post = get_object_or_404(Posts,slug=slug)
	ret_dict = get_exchange_rates()
	ret_dict['posts']=posts
	return render(request,'post.html',ret_dict)
