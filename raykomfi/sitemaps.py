from django.contrib.sitemaps import Sitemap
from .models import Post
from django.urls import reverse


class PostSitemap(Sitemap):
	changefreq = "daily"
	priority = 0.9
		
	def items(self):
		return Post.objects.filter(isActive=True)
		
	def lastmod(self, obj):
		return obj.updated

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['raykomfi:raykomfi-home', 'raykomfi:about', 'raykomfi:user-register', 'raykomfi:user-signin', 'raykomfi:user-register-withnosignup', 'raykomfi:usage-terms']

    def location(self, item):
        return reverse(item)