from django.db import models as m
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField, ModificationDateTimeField
# Create your models here.

class Thing(m.Model):
	uri = m.URLField(verify_exists=False, unique=True)
	slug = AutoSlugField(populate_from="uri", unique=True, )
	def __str__(self):
		return self.uri;
	
	@m.permalink
	def get_absolute_url(self):
		return('thing_detail', [self.slug])

class Review(m.Model):
	date_created = CreationDateTimeField()
	date_modified = ModificationDateTimeField()
	title = m.CharField(max_length=128)
	text = m.TextField()
	rating = m.IntegerField()
	author = m.ForeignKey(User)
	reviewed_uri = m.ForeignKey(Thing)
	
	@m.permalink
	def get_absolute_url(self):
		return('review_detail', [str(self.id)])

class ExtendedReview(Review):
	extra = m.TextField()


#Set the first_name to the first part of the email address
from django.db.models.signals import post_save, pre_save

def user_first_name(sender, instance, created, **kwargs):
	if created:
		instance.firstname = instance.email.rsplit("@",1)[0][:30]
		instance.save()

post_save.connect(user_first_name, sender=User)

##cache gravatar md5
#import urllib, hashlib
#class UserProfile(m.Model):
	## This field is required.
	#user = m.OneToOneField(User)
	#gravatar_hash = m.CharField(max_length=32)

#def create_user_profile(sender, instance, created, **kwargs):
	#if created:
		#gravatar_hash = hashlib.md5(instance.email.lower()).hexdigest()
		#UserProfile.objects.create(user=instance)


#post_save.connect(create_user_profile, sender=User)
