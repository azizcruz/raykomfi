from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
	changefreq = "daily"
	priority = 0.9
		
	def items(self):
		return Post.objects.filter(isActive=True)
		
	def lastmod(self, obj):
		return obj.updated