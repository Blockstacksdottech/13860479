"""exchanger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from exchanger_app.views import *
from blog.views import *
from custom_admin.views import *
import exchanger.settings as settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index,name='app_index'),
    path('exchange',exchange_pannel,name='pannel'),
    path('how-it-works',howitworks,name='how_it_work'),
    path('checkup',checkup,name='checkup'),
    path('contact',contact,name='contact'),
    path('subscribe',subscribe,name='subscribe'),
    path('blog',view_blog,name='blog'),
    path('view/<str:slug>',view_post,name='post'),
    path('details/<str:idd>',check,name='process'),
    path('check/<str:idd>',check,name='check'),
    path('start',start,name='start'),
    path('startupdater',start_updater),
    path('faq',faq),
    path('custadmin',view_login),
    path('verfadmin',verify_login),
    path('pannel',show_pannel),
    path('logout',log_out),
    path('blog/logout',blog_log_out),
    path('blog/admin',blog_admin),
    path('blog/login',blog_login),
    path('blog/tags',tags),
    path('blog/add',adder),
    path('blog/add_post',add_post),
    path('blog/addtag',add_tag),
    path('blog/deletetag/<str:tag>',delete_tag),
    path('blog/modify/<str:slug>',modify),
    path('blog/delete/<str:slug>',delete_post),
    path('blog/modify_post',modify_post),
    path('settings',view_settings),
    path('settings/changemin',change_min)

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
