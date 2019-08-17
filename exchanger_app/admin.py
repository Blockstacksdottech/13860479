from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Task)
admin.site.register(Transaction)
admin.site.register(Currencies)
admin.site.register(Listener)
admin.site.register(Prices)
