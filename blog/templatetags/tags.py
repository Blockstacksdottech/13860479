from django import template
register = template.Library()



@register.simple_tag
def define(val=None):
	return val

@register.simple_tag
def increment(val=None):
	val += 1
	return val

@register.simple_tag
def mod_res(val=None):
	return val % 3