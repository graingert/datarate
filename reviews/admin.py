import reviews.models as m
from django.contrib.admin import site, ModelAdmin

class ReviewAdmin(ModelAdmin):
	list_display = ('rating', '__unicode__')
	pass

site.register(m.Review, ReviewAdmin)
site.register(m.Thing)

