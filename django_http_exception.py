#encoding: UTF-8
#http://devwithpassion.com/felipe/manipulando-erros-http-403-permissao-negada-no-django/
_LICENSE ="""
NEW BSD LICENSE: http://www.opensource.org/licenses/bsd-license.php

Copyright (c) 2009, Felipe R. Prenholato
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the Felipe R. Prenholato nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from django.conf import settings
from django.core.exceptions import ViewDoesNotExist
from django.http import HttpResponse
from django.template import RequestContext,Template,loader,TemplateDoesNotExist
from django.utils.importlib import import_module
import httplib

class HttpException(Exception):
	""" Exception for Http Errors"""
	def __init__(self, message, status=500):
		self.status = status
		super(HttpException, self).__init__(message)

class HttpExceptionMiddleware(object):
	"""
	Replace Status code raises for a {{status}}.html rendered template
	"""
	def process_exception(self, request, exception):
		"""
		Render a {{status}}.html template or a hardcoded html as status page, but only if
		exception is instance of HttpException class
		"""
		# we need to import to use isinstance
		from django_http_exception import HttpException
		if not isinstance(exception,HttpException):
			# Return None make that django reraise exception:
			# http://docs.djangoproject.com/en/dev/topics/http/middleware/#process_exception
			return None

		print exception.status
	
		try:
			# Handle import error but allow any type error from view
			callback = getattr(import_module(settings.ROOT_URLCONF),'handler' + str(exception.status))
			return callback(request,exception)
		except (ImportError,AttributeError),e:
			# doesn't exist a handler{{status}}, try get template
			try:
				t = loader.get_template(str(exception.status) + '.html')
			except TemplateDoesNotExist:
				# doesn't exist a template in path, use hardcoded template
				t = Template("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">
<HTML>
  <HEAD>
    <TITLE>
    {% if message %}
		{{message}}
	{% else %}
    Sorry {{w3cname}} error to {{ request.META.PATH }}.
    {% endif%}
    </TITLE>
  </HEAD>
  <BODY>
    <h2>{{w3cname}}</h2>
    <p>{% if message %}
		{{message}}
	{% else %}
    Sorry {{w3cname}} error to {{ request.META.PATH }}.
    {% endif%}</p>
  </BODY>
</HTML>""")

		# now use context and render template      
		c = RequestContext(request, {
		'message': exception.message,
		'w3cname': httplib.responses.get(exception.status, str(exception.status)),
		'status_code': exception.status,
		})
      
		return HttpResponse(t.render(c), status=exception.status)
