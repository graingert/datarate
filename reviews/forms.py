from django.forms import ModelForm, HiddenInput
from models import Thing, Review, UserProfile
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
		
class ProfileForm(ModelForm):
	class Meta:
		model = UserProfile
		fields = ("nickname",)
