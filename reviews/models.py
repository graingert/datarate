from django.conf import settings
from django.db import models as m
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField, ModificationDateTimeField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save, pre_save
from django.db.models import Count, Sum
from GChartWrapper import Pie

import thingvalidator

import urllib, hashlib, urlparse, urllib2
from rdflib import ConjunctiveGraph, Namespace, exceptions
from rdflib import URIRef, RDFS, RDF, BNode
import bleach
# Create your models here.

class StepValidator():
	def __init__(self, min_value, step):
		self.min_value = min_value
		self.step = step
		
	def __call__(self, value):
		if (value - self.min_value)% self.step != 0:
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
	label = m.CharField(max_length=30)
	
	def __unicode__(self):
		return self.label
	
	@m.permalink
	def get_absolute_url(self):
		return('thing_detail', [self.slug])
	
	@property
	def graph(self):
		if not hasattr(self, "_graph"):
			graph = ConjunctiveGraph()
			graph.parse(self.uri)
			self._graph = graph
		return self._graph
		#return getattr(self, "_graph", self.build_graph())
	
	def get_label(self):
		return unicode(self.graph.label(URIRef(self.uri), urlparse.urlparse(self.uri).path))
		
		
	def save(self):
		self.label = self.get_label()[:30]
		super(Thing, self).save()
	
	def description(self):
		desc = self.graph.value(
			subject=URIRef(self.uri),
			predicate=URIRef("http://purl.org/dc/terms/description"),
			object=None,
			default="No description"
		)
		desc = bleach.clean(unicode(desc), tags = bleach.ALLOWED_TAGS + ["p",])
		return desc
	
	def histogram(self):
		return self.review_set.values('rating').order_by('-rating').annotate(count = Count('rating'))
		
	def chart(self):
		labels=[]
		count=[]
		colors=[]
		
		histogram = self.histogram()
		
		style_map = {
				-3:
					{
						"label" :"Terrible",
						"color": "CC0000" 
					},
				-1 : {
						"label" :"Bad",
						"color": "CC6600" 
					},
				1 : {
						"label" :"Good",
						"color": "99CC00" 
					},
				3 : {
						"label" :"Great",
						"color": "00CC00" 
					},
			}
		
		
		for point in histogram:
			style = style_map[point["rating"]]
			
			labels.append(style["label"])
			colors.append(style["color"])
			count.append(point["count"])
		
		return unicode(Pie(count,apiurl="https://chart.googleapis.com/chart?").color(*colors).label(*labels))
	
	@classmethod
	def construct_from_uri(cls, uri):
		return thingvalidator.construct_from_uri(uri)

class Review(m.Model):
	date_created = CreationDateTimeField()
	date_modified = ModificationDateTimeField()
	#title = m.CharField(max_length=128)
	rating = RangeField(min_value=-3, max_value = 3, step = 2)
	text = m.TextField()
	author = m.ForeignKey(User, editable=False)
	reviewed_uri = m.ForeignKey(Thing)
	
	def get_absolute_url(self):
		thing_url = self.reviewed_uri.get_absolute_url()
		return thing_url + '#review-' + str(self.id)
		
	def __unicode__(self):
		return self.text[:140]
		
	class Meta:
		unique_together = ("author", "reviewed_uri")

class ExtendedReview(Review):
	extra = m.TextField()

class UserProfile(m.Model):
	# This field is required.
	user = m.OneToOneField(User)
	gravatar_hash = m.CharField(max_length=32)
	nickname = m.CharField(max_length=30)
    
    #https://en.gravatar.com/site/implement/images/python/
	def gravatar_url(self, size=80):
		gravatar_url = "https://secure.gravatar.com/avatar/" + self.gravatar_hash + "?"
		gravatar_url += urllib.urlencode({'d':"retro", 's':str(size)})
		return gravatar_url
	
	def big_gravatar_url(self):
		return self.gravatar_url(size=512)
	
	def __unicode__(self):
		return self.user.email
	
	@m.permalink
	def get_absolute_url(self):
		return('profile', [self.pk])
	
		

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
