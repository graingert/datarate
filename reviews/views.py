# Create your views here.
from reviews.models import *
from django.views.generic import *
import urllib

class ReviewableDetailView(DetailView):
	queryset = Reviewable_URI.objects.all()

	def get_object(self):
		encoded_uri = self.kwargs["uri"]
		uri = urllib.unquote(encoded_uri)
		return Reviewable_URI(reviewed_uri = uri)
