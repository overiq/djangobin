from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.flatpages import views as flat_views
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import SnippetSitemap, FlatPageSitemap


# app_name = 'djangobin'

sitemaps = {
    'snippets': SnippetSitemap,
    'flatpages': FlatPageSitemap,
}


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/(?P<username>[A-Za-z0-9]+)/$', views.profile, name='profile'),
    url('^trending/$', views.trending_snippets, name='trending_snippets'),
    url('^trending/(?P<language_slug>[\w]+)/$', views.trending_snippets, name='trending_snippets'),
    url('^(?P<snippet_slug>[\d]+)/$', views.snippet_detail, name='snippet_detail'),
    url('^tag/(?P<tag>[\w-]+)/$', views.tag_list, name='tag_list'),
    url('^download/(?P<snippet_slug>[\d]+)/$', views.download_snippet, name='download_snippet'),
    url('^raw/(?P<snippet_slug>[\d]+)/$', views.raw_snippet, name='raw_snippet'),
    url('^contact/$', views.contact, name='contact'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^userdetails/$', views.user_details, name='user_details'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}'
        r'-[0-9A-Za-z]{1,20})/$',
        views.activate_account, name='activate'),

    # password reset URLs

    url('^password-reset/$', auth_views.password_reset,
        {'template_name': 'djangobin/password_reset.html',
         'email_template_name': 'djangobin/email/password_reset_email.txt',
         'subject_template_name': 'djangobin/email/password_reset_subject.txt',
         'post_reset_redirect': 'djangobin:password_reset_done',
         },
        name='password_reset'),

    url('^password-reset-done/$', auth_views.password_reset_done,
        {'template_name': 'djangobin/password_reset_done.html', },
        name='password_reset_done'),

    url(r'^password-confirm/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}'
        r'-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'template_name': 'djangobin/password_reset_confirm.html',
         'post_reset_redirect': 'djangobin:password_reset_complete'},
        name='password_reset_confirm'),

    url(r'password-reset-complete/$',
        auth_views.password_reset_complete,
        {'template_name':
             'djangobin/password_reset_complete.html'},
        name='password_reset_complete'),

    # password change URLs

    url(r'^password-change/$', auth_views.password_change,
        {'template_name': 'djangobin/password_change.html',
         'post_change_redirect': 'djangobin:password_change_done'},
        name='password_change'
        ),

    url(r'^password-change-done/$', auth_views.password_change_done,
        {'template_name': 'djangobin/password_change_done.html'},
        name='password_change_done'
        ),

    url('^settings/$', views.settings, name='settings'),
    url('^delete/(?P<snippet_slug>[\d]+)/$', views.delete_snippet, name='delete_snippet'),
    url('^search/$', views.search, name='search'),
    url(r'^about/$', flat_views.flatpage, {'url': '/about/'}, name='about'),
    url(r'^eula/$', flat_views.flatpage, {'url': '/eula/'}, name='eula'),
    url(r'^sitemap\.xml/$', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]