from django.db import models

# Create your models here.


class User(models.Model):
	username = models.CharField(max_length=255,unique=True)
	password = models.CharField(max_length=255)

	def __str__(self):
		return self.username

class Settings(models.Model):
	activated =  models.BooleanField(default=True)
	service_fee = models.FloatField(default=0)
	min_amount = models.FloatField(default=0)
	max_amount  =  models.FloatField(default=0)
	delay = models.IntegerField(default=0)

	def __str__(self):
		return str(self.activated)


class Currencies_s(models.Model):
	setting = models.ForeignKey(Settings,on_delete=models.CASCADE)
	currency = models.CharField(max_length=50)
	activated = models.BooleanField(default=True)

	def __str__(self):
		return self.currency