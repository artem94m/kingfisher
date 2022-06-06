from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^articles/([0-9]{4})/$', 'news.views.year_archive'),
    url(r'^articles/([0-9]{4})/([0-9]{2})/$', 'news.views.month_archive'),
    url(r'^admin/$', 'news.views.article_detail'),
)