from django.db import models as m
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField, ModificationDateTimeField
from django.core.validators import MaxValueValidator, MinValueValidator

import urllib, hashlib
from rdflib import ConjunctiveGraph, Namespace, exceptions
from rdflib import URIRef, RDFS, RDF, BNode
import bleach
# Create your models here.

class StepValidator():
	def __init__(min_value, step):
		self.min_value = min_value
		self.step = step
		
	def __call__(self, value):
		if (value - min_value)% step != 0:
			raise ValidationError(u'%s does not have the correct step' % value)
		

class RangeField(m.IntegerField):
	def __init__(self, min_value, max_value, step=None, *args, **kwargs):
		validators = kwargs.setdefault("validators",[])
		validators += [MinValueValidator(min_value), MaxValueValidator(max_value)]
		if step:
			validators.append(StepValidator(min_value, step))
		super(RangeField, self).__init__(*args, **kwargs)
		

class Thing(m.Model):
	uri = m.URLField(verify_exists=False, unique=True)
	slug = AutoSlugField(populate_from="uri", unique=True, )
	def __unicode__(self):
		return self.label();
	
	@m.permalink
	def get_absolute_url(self):
		return('thing_detail', [self.slug])
	
	@property
	def graph(self):
		if not hasattr(self, "_graph"):
			self._graph = ConjunctiveGraph()
			self._graph.parse(self.uri)
		return self._graph
		#return getattr(self, "_graph", self.build_graph())
	
	def label(self):
		return unicode(self.graph.label(URIRef(self.uri), self.uri))
	
	def description(self):
		desc = self.graph.value(
			subject=URIRef(self.uri),
			predicate=URIRef("http://purl.org/dc/terms/description"),
			object=None,
			default="No description"
		)
		desc = bleach.clean(unicode(desc), tags = bleach.ALLOWED_TAGS + ["p",])
		return desc
		

class Review(m.Model):
	date_created = CreationDateTimeField()
	date_modified = ModificationDateTimeField()
	#title = m.CharField(max_length=128)
	text = m.TextField()
	rating = RangeField(min_value=-3, max_value = 3, step = 2)
	author = m.ForeignKey(User, editable="false")
	reviewed_uri = m.ForeignKey(Thing)
	
	unique_together = ("author", "reviewed_uri")
	
	def get_absolute_url(self):
		thing_url = self.reviewed_uri.get_absolute_url()
		return thing_url + '#review-' + str(self.id)
		
	def __unicode__(self):
		return self.text[:140]

class ExtendedReview(Review):
	extra = m.TextField()

from django.db.models.signals import post_save, pre_save

class UserProfile(m.Model):
    # This field is required.
    user = m.OneToOneField(User)
    gravatar_hash = m.CharField(max_length=32)
    nickname = m.CharField(max_length=30)
    
    def gravatar_url(self):
		return "https://secure.gravatar.com/avatar/" + self.gravatar_hash
		

"""
Set the first_name to the first part of the email address and cache the
gravatar md5 to avoid recalculating it
"""

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(
			user = instance,
			nickname = instance.email.rsplit("@",1)[0][:30],
			gravatar_hash = hashlib.md5(instance.email.lstrip().lower()).hexdigest()
		)

post_save.connect(create_user_profile, sender=User)
