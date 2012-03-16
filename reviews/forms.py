from django.forms import ModelForm, HiddenInput
from models import Review, Thing
from django.core.exceptions import ValidationError
from rays.widgets import RangeInput


import urlparse


class ReviewForm(ModelForm):
	class Meta:
		model = Review
		exclude = ("author",)
		widgets = {
			'rating': RangeInput(min_value=-3, max_value=3, step=2), #uses 4 states preventing any "on the fence choices"
			'reviewed_uri' : HiddenInput(),
		}

class ThingForm(ModelForm):
	class Meta:
		model = Thing
		fields = ("uri",)
		
	def clean_uri(self):
		data = self.cleaned_data["uri"]
		
		if urlparse.urlparse(data).netloc == "id.southampton.ac.uk":
			return data
		else:
			raise ValidationError("Not an acceptable netloc")
		
