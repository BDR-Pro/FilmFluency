from django.contrib.sitemaps import Sitemap
from learning.models import Movie

class MovieSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    limit = 200
    
    def items(self):
        return Movie.objects.all()

    def lastmod(self, obj):
        return obj.last_updated()