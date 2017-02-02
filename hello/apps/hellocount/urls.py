from django.conf.urls import url
from hellocount import views

urlpatterns = [
    url(r'^$', views.post_data, name='home'),
    url(r'^player/(?P<rawname>[a-zA-Z]+)/$', views.get_by_name, name='player_by_name'),
    url(r'^leaders/(?P<realm>[a-zA-Z]+)/$', views.leaders, name='leaders'),
    url(r'^leaders/$', views.leaders, name='leaders_all'),
    url(r'^render_leaders/$', views.render_leaders, name='render'),
    url(r'^guilds/$', views.by_guild, name='guilds'),
]
