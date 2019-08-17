from django.db import models

# Create your models here.


class Task(models.Model):
	transaction_id = models.CharField(max_length = 1000)
	action =  models.CharField(max_length = 300)
	status = models.CharField(max_length = 300)

	def __str__(self):
		return self.transaction_id

class Transaction(models.Model):
	transaction_id = models.CharField(max_length=1000)
	return_address = models.CharField(max_length=1000)
	refund_address = models.CharField(max_length=1000)
	recv_address = models.CharField(max_length=1000)
	in_currency = models.CharField(max_length=10)
	out_currency = models.CharField(max_length=10)
	amount_in = models.BigIntegerField(default=0)
	fees = models.IntegerField(default=5)
	amount_out = models.BigIntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	hash_tr = models.CharField(max_length=1000,default = None)

	def __str__(self):
		return self.out_currency + ' ' + self.return_address
	def save(self, *args, **kwargs):
		if len(Task.objects.filter(transaction_id = self.transaction_id)) != 0:
			pass
		else:
			t = Task.objects.create(transaction_id = self.transaction_id,
			action = 'Waiting for funds',
			status = 'runing'
			)
			t.save()
		super(Transaction, self).save(*args, **kwargs)


class Currencies(models.Model):
	currency = models.CharField(max_length=10)
	test_address = models.CharField(max_length=1000)
	balance = models.BigIntegerField(default=0)

	def __str__(self):
		return self.currency + ' ' + str(self.balance)

class Prices(models.Model):
	currency = models.CharField(max_length=10)
	price = models.FloatField(default=0)

	def __str__(self):
		return self.currency + ' ' + str(self.price)

class Listener(models.Model):
	name = models.CharField(max_length = 300)
	status = models.BooleanField(default=False)

	def __str__(self):
		return self.name
