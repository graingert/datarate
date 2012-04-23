#Based on some ideas from https://github.com/yangsquared/HyperThing

import reviews.models

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

import urllib, hashlib, urlparse, urllib2
from rdflib import ConjunctiveGraph, Namespace, exceptions
from rdflib import URIRef, RDFS, RDF, BNode

from xml.sax import SAXException

class ThingException(Exception):
	def __init__(self, uri, message="{uri} caused an Unknown Error"):
		self.uri = uri
		message = message.format(uri=uri)
		super(ThingException, self).__init__(message)
	
class URIException(ThingException):
	pass
	
class UnsuportedURIException(URIException):
	def __init__(self, uri):
		super(UnsuportedURIException, self).__init__(uri, "{uri} is not supported by this system")
	
class UnresovableURIException(URIException):
	def __init__(self, uri):
		super(UnresovableURIException, self).__init__(uri, "{uri} is not resolvable")

class DataException(ThingException):
	pass

class InvalidResourceException(DataException):
	def __init__(self, uri):
		super(InvalidResourceException, self).__init__(uri, "{uri} is not a valid RDF resource")
	
class NoDataException(DataException):
	def __init__(self, uri):
		super(NoDataException, self).__init__(uri, "{uri} does not contain any data about {uri}")

def construct_from_uri(uri):
	Thing = reviews.models.Thing
	try:
		#try to get a pre-existing object from the DB.
		return Thing.objects.get(uri=uri)
	except ObjectDoesNotExist:
		#Right we don't have one, now to validate the Thing.
		
		netloc_whitelist = getattr(settings, 'REVIEWS_NETLOC_WHITELIST', ("id.southampton.ac.uk",))
		scheme_whitelist = getattr(settings, 'REVIEWS_SCHEME_WHITELIST', ("http","https"))
		
		parseduri = urlparse.urlparse(uri)
		
		if (parseduri.netloc not in netloc_whitelist) or (parseduri.scheme not in scheme_whitelist):
			raise UnsuportedURIException(uri)
		
		thing = Thing(uri=uri)
		
		try:
			thing.graph
		except urllib2.URLError:
			raise UnresovableURIException(uri)
		except SAXException:
			raise InvalidResourceException(uri)
		except:
			raise ThingException(uri)

		try:
			thing.graph.predicate_objects(URIRef(uri)).next()
		except StopIteration:
			raise NoDataException(uri)
		
		#Okay it looks like we can add it to the db
		thing.save()
		return thing
