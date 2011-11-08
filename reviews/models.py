from django.db import models as m
from django.contrib.auth import models as authm
# Create your models here.

class Review(m.Model):
	reviewed_uri = m.URLField(verify_exists=False)
	datetime = m.DateTimeField(auto_now_add=True)
	title = m.CharField(max_length=128)
	text = m.TextField()
	rating = m.IntegerField()
	author = m.ForeignKey(authm.User)
	
	@m.permalink
	def get_absolute_url(self):
		return('review_detail', [str(self.id)])
