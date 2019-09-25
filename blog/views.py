from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from .models import *
from exchanger_app.models import *
from django.core.files.storage import FileSystemStorage
from custom_admin.models import *


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
	populars = Posts.objects.all().order_by('-clicked')
	ret_dict = get_exchange_rates()
	ret_dict['posts']=posts
	ret_dict['populars'] = populars
	tags = Tags.objects.all()
	ret_dict['tags'] = tags
	return render(request,'blog_main.html',ret_dict)

def view_post(request,slug):
	post = get_object_or_404(Posts,slug=slug)
	populars = Posts.objects.all().order_by('-clicked')
	post.clicked += 1
	ret_dict = get_exchange_rates()
	ret_dict['post']=post
	ret_dict['populars'] = populars
	
	return render(request,'post.html',ret_dict)

def blog_admin(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		posts = Posts.objects.all().order_by('-date')
		return render(request,'cms/all_posts.html',{'posts':posts})

def tags(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		tags = Tags.objects.all()
		return render(request,'cms/tags_add.html',{'tags':tags})

def adder(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		tags  = Tags.objects.all()
		return render(request,'cms/create_post.html',{'tags':tags})


def add_tag(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		if request.method == 'POST':
			name= request.POST.get('name')
			title = request.POST.get('title')
			desc = request.POST.get('desc')
			keyword =  request.POST.get('key')
			t = Tags.objects.create(
				name = name,
				meta_title = title,
				meta_desc = desc,
				keyword = keyword
			)
			t.save()
			return redirect('/blog/tags')

def delete_tag(request,tag):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		t = get_object_or_404(Tags,name = tag)
		t.delete()
		return redirect('/blog/tags')




def add_post(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		if request.method == 'POST' and request.FILES['myfile'] :
			myfile = request.FILES['myfile']
			title = request.POST.get('title')
			description =request.POST.get('description')
			tag = request.POST.get('tag')
			m_title = request.POST.get('metatitle')
			m_desc = request.POST.get('metadesc')
			m_key = request.POST.get('metakey')
			fs = FileSystemStorage()
			
			filename = fs.save(myfile.name, myfile)
			uploaded_file_url = fs.url(filename)
			print(uploaded_file_url)
			p = Posts.objects.create(
				title = title,
				small_description = m_desc,
				content = description,
				image = uploaded_file_url,
				tag = tag,
				meta_title = m_title,
				meta_key = m_key
			)
			p.save()
			return redirect('/blog/admin')

def modify_post(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		if request.method == 'POST' and request.FILES.get('myfile',True) :
			myfile = request.FILES.get('myfile','')
			slug = request.POST.get('slug')
			title = request.POST.get('title')
			description =request.POST.get('description')
			print(description)
			tag = request.POST.get('tag')
			m_title = request.POST.get('metatitle')
			m_desc = request.POST.get('metadesc')
			m_key = request.POST.get('metakey')
			
			p = get_object_or_404(Posts,slug=slug)
			p.title = title
			if len(description) == 0 and len(p.content) == 0:
				pass
			else:
				if len(p.content) != 0:
					if len(description) != 0:
						p.content = description
					else:
						pass
				else:

					p.content = description
			p.tag = tag
			if myfile == '':
				pass
			else:
				fs = FileSystemStorage()
				filename = fs.save(myfile.name, myfile)
				uploaded_file_url = fs.url(filename)
				print(uploaded_file_url)
				p.image = uploaded_file_url
			p.meta_title = m_title
			p.meta_key = m_key
			p.small_description = m_desc
			p.save()
			return redirect('/blog/admin')


def add_dash(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		return render(request,'cms/create_post.html')

def modify(request,slug):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		
		post = get_object_or_404(Posts,slug=slug)
		tags = Tags.objects.all()
		return render(request,'cms/modify_post.html',{'post':post,'tags':tags})

def delete_post(request,slug):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		
		post = get_object_or_404(Posts,slug=slug)
		post.delete()
		return redirect('/blog/admin')

def view_settings(request):
	username = request.session.get('user','')
	if username == '':
		return redirect('/blog/login')
	else:
		setting = Settings.objects.all()[0]
		ret_dict  = {
			'stats':setting.activated,
			'fee':setting.service_fee,
			'min':setting.min_amount,
			'max':setting.max_amount,
			'delay':setting.delay
			
		}
		coins = setting.currencies_s_set.all()
		for x in coins:
			ret_dict[x.currency] = x.activated
		return render(request,'settings.html',ret_dict)

def blog_login(request):
	if request.method == 'POST':
		username = request.POST.get('username','')
		password = request.POST.get('password','')

		if username == '' or password == '':
			return render(request,'login.html',{'message':'empty field'})

		usr = User.objects.filter(username =  username )
		if len(usr) != 0:
			usr = usr[0]
			if password == usr.password:
				request.session.set_expiry(0)
				request.session['user'] = usr.username
				return  redirect('/blog/admin')
			else:
				return render(request,'login.html',{'message':'password is incorrect'})
				
		else:
			return render(request,'login.html',{'message':'user not found'})
		
	else:
		return render(request,'login.html')


def blog_log_out(request):
	del request.session['user']
	return redirect('/blog/admin')







