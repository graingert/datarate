"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils import simplejson as json
import requests
import random
import urllib

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class SampleThingLoading(TestCase):
	def setUp(self):
		self.uris = []
		r= requests.get('http://sparql.data.southampton.ac.uk/?query=PREFIX+soton%3A+<http%3A%2F%2Fid.southampton.ac.uk%2Fns%2F>%0D%0APREFIX+foaf%3A+<http%3A%2F%2Fxmlns.com%2Ffoaf%2F0.1%2F>%0D%0APREFIX+skos%3A+<http%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23>%0D%0APREFIX+geo%3A+<http%3A%2F%2Fwww.w3.org%2F2003%2F01%2Fgeo%2Fwgs84_pos%23>%0D%0APREFIX+rdfs%3A+<http%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23>%0D%0APREFIX+org%3A+<http%3A%2F%2Fwww.w3.org%2Fns%2Forg%23>%0D%0APREFIX+spacerel%3A+<http%3A%2F%2Fdata.ordnancesurvey.co.uk%2Fontology%2Fspatialrelations%2F>%0D%0APREFIX+ep%3A+<http%3A%2F%2Feprints.org%2Fontology%2F>%0D%0APREFIX+dct%3A+<http%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F>%0D%0APREFIX+bibo%3A+<http%3A%2F%2Fpurl.org%2Fontology%2Fbibo%2F>%0D%0APREFIX+owl%3A+<http%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23>%0D%0A%0D%0ASELECT+DISTINCT+%3Fs+WHERE+{%0D%0A++++%3Fs+%3Fp+%3Fo+.%0D%0A}&output=json')
		dirty_uris = json.loads(r.text)
		for result in dirty_uris["results"]["bindings"]:
			if result["s"]["type"]=="uri":
				self.uris.append(result["s"]["value"])
		
		self.test_uri = lambda uri: self.client.get("/thing.json?{data}".format(data=urllib.urlencode({"uri":uri})))
	
	def test_bad(self):
		resp = self.test_uri("file:///etc/passwords")
		self.assertEqual(resp.status_code, 400)
	
	def test_not_found(self):
		resp = self.test_uri("http://id.southampton.ac.uk/404")
		self.assertEqual(resp.status_code, 502)

	#def test_loading_things(self):
		#for uri in self.uris:
			#resp = self.test_uri(uri)
			#self.assertIn(resp.status_code, (302,404,502))
