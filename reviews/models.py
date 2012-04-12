from django.db import models as m
from django.contrib.auth.models import User
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField, ModificationDateTimeField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save, pre_save
from django.db.models import Count, Sum
from GChartWrapper import Pie
from reviews import SCALE, SCORE_MAP
import thingvalidator

import urllib, hashlib, urlparse, urllib2
from rdflib import ConjunctiveGraph, Namespace, exceptions
from rdflib import URIRef, RDFS, RDF, BNode
import bleach
import math
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

#http://www.evanmiller.org/how-not-to-sort-by-average-rating.html
def ci_lower_bound(pos, neg):
	n = pos+neg
	if n == 0:
		return 0
	return ((pos + 1.9208) / (n) -  1.96 * math.sqrt((pos*neg) / (n) + 0.9604) / (n)) / (1 + 3.8416 / (n))

class Thing(m.Model):
	uri = m.URLField(verify_exists=False, unique=True)
	slug = AutoSlugField(populate_from="uri", unique=True, )
	label = m.CharField(max_length=30)
	ci_lower_bound = m.FloatField(default = 0)
	
	for score in range(SCALE):
		locals()['review_%s_count' % str(score)] = m.IntegerField(default=0)
	
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
		
	def chart(self):
		labels=[]
		counts=[]
		colors=[]
		
		
		for point in range(SCALE):
			style = SCORE_MAP[point]
			
			labels.append(style["label"])
			colors.append(style["color"])
			counts.append(getattr(self, "review_%s_count" % str(point)))
		
		return unicode(Pie(counts,apiurl="https://chart.googleapis.com/chart?").color(*colors).label(*labels))
	
	def table(self):
		points = []
		total = 0
		for point in range(SCALE):
			style = SCORE_MAP[point]
			count = getattr(self, "review_%s_count" % str(point))
			
			if count > 0:
				points.append({
					"label" : style["label"],
					"count" : count,
					"color" : style["color"],
				})
				
				total += count
		
		if total == 0:
			return points
			
		for point in points:
			point["percentage"] = (point["count"]/float(total)) * 100.0
			
		return points
		
	@classmethod
	def construct_from_uri(cls, uri):
		return thingvalidator.construct_from_uri(uri)
		
	def recalculate_rating_counts(self):
		rating_counts = self.review_set.values('rating').order_by('-rating').annotate(count = Count('rating'))
		
		#clear all the values
		for point in range(SCALE):
			setattr(self, "review_%s_count" % str(point), 0)
		
		#set values based on calculated rating counts
		#and calculate statistics required for ci_lower_bound
		
		max_positive = SCALE-1
		pos = 0
		neg = 0
		for rating_count in rating_counts:
			rating = rating_count["rating"]
			count = rating_count["count"]
			
			neg_rating = (max_positive - rating)
			pos_rating = rating
			
			neg += neg_rating
			pos += pos_rating
			setattr(self, "review_%s_count" % str(rating), count)
		
		self.ci_lower_bound = ci_lower_bound(pos, neg)
		self.save()

class Review(m.Model):
	date_created = CreationDateTimeField()
	date_modified = ModificationDateTimeField()
	#title = m.CharField(max_length=128)
	rating = RangeField(min_value=0, max_value = SCALE-1, step = 1)
	text = m.TextField(verbose_name="Detailed Review")
	author = m.ForeignKey(User, editable=False)
	reviewed_uri = m.ForeignKey(Thing)
	mentioned = m.TextField(blank=True)
	
	def get_absolute_url(self):
		thing_url = self.reviewed_uri.get_absolute_url()
		return thing_url + '#review-' + str(self.id)
		
	def rating_label(self):
		return SCORE_MAP[self.rating]["label"]
	
	def __unicode__(self):
		return self.text[:140]
		
	class Meta:
		unique_together = ("author", "reviewed_uri")
		
	

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
		
		
def recalculate_rating_counts(sender, instance, created, **kwargs):
	instance.reviewed_uri.recalculate_rating_counts()
	
post_save.connect(recalculate_rating_counts, sender=Review)

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
