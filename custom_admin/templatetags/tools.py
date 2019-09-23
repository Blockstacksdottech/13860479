from django import template
from exchanger_app.models import *
register = template.Library()



@register.simple_tag
def getindex(lst=None,index=None):
	print(lst)
	return lst[index]

@register.simple_tag
def checkstatus(idd=None):
	t = Task.objects.filter(transaction_id = idd)[0]
	if t.status == 'waiting':
		return 1
	elif t.status == 'exchanging':
		return 2
	else:
		return 3
