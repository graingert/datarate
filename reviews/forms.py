from django.forms import ModelForm, HiddenInput, MultipleHiddenInput, SelectMultiple, CharField
from models import Thing, Review, UserProfile
from django_extrawidgets.widgets import RangeInput
from reviews import SCALE, SCORE_MAP


class ReviewForm(ModelForm):
	class Meta:
		model = Review
		exclude = ("author",)
		widgets = {
			'rating': RangeInput(min_value=0, max_value=SCALE-1, step=1), #uses 4 states preventing any "on the fence choices"
			'reviewed_uri' : HiddenInput(),
			'mentioned' : HiddenInput(),
		}
		
class ProfileForm(ModelForm):
	class Meta:
		model = UserProfile
		fields = ("nickname",)
