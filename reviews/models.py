from django.db import models as m
from django.contrib.auth import models as authm
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
	author = m.ForeignKey(authm.User)
	reviewed_uri = m.ForeignKey(Thing)
	
	@m.permalink
	def get_absolute_url(self):
		return('review_detail', [str(self.id)])

class ExtendedReview(Review):
	extra = m.TextField()
