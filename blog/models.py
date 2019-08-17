from django.db import models
from django.template.defaultfilters import slugify
import random

# Create your models here.

class Posts(models.Model):
	title = models.CharField(max_length=250)
	slug = models.SlugField(unique=True)
	small_description = models.CharField(max_length=500)
	content = models.TextField()
	image = models.ImageField(upload_to = 'assets/media/')
	date = models.DateTimeField()

	def save(self, *args, **kwargs):
		if not self.id:
			# Newly created object, so set slug
			self.slug = slugify(self.title) 
			if len(Posts.objects.filter(slug=self.slug)) >= 1:
				self.slug = slugify(self.title) + str(random.randrange(1,1000000))
			else:
				pass
				

		super(Posts, self).save(*args, **kwargs)
	
		def __str__(self):
			return self.title