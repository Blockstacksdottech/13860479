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
    path('details/<str:idd>',view_tr,name='process'),
    path('check/<str:idd>',check,name='check'),
    path('start',start,name='start')

]
