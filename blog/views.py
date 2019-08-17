from django.shortcuts import render,HttpResponse,get_object_or_404
from .models import *

# Create your views here.


def view_blog(request):
	posts = Posts.objects.all()
	ret_dict = {
		'posts':posts
	}
	return render(request,'blog_main.html',ret_dict)

def view_post(request,slug):
	post = get_object_or_404(Posts,slug=slug)
	ret_dict = {
		'post':post
	}
	return render(request,'post.html',ret_dict)
