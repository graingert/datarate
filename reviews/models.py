from django.db import models as m
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField, ModificationDateTimeField
import urllib, hashlib
from rdflib import ConjunctiveGraph, Namespace, exceptions
from rdflib import URIRef, RDFS, RDF, BNode
import bleach
# Create your models here.

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
	rating = m.IntegerField()
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
