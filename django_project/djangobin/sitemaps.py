from django.contrib.sitemaps import Sitemap
from django.contrib.flatpages.models import FlatPage
from .models import Snippet


class SnippetSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return Snippet.objects.all()


class FlatPageSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return FlatPage.objects.all()