from django.conf.urls import url
from hellocount import views

urlpatterns = [
    url(r'^$', views.post_data, name='home'),
    url(r'.*html$', views.redir_404, name='go_home'),
    url(r'^realmwar/$', views.realmwar, name='realmwar'),
    url(r'^realmwar2/$', views.realmwar2, name='realmwar2'),
    url(r'^update_df/$', views.update_df, name='update_df'),
    url(r'^update_keep/$', views.update_keep, name='update_keep'),
    url(r'^render_keeps/$', views.render_keeps, name='render_keeps'),
    url(r'^player/(?P<rawname>[a-zA-Z]+)/$', views.get_by_name, name='player_by_name'),
    url(r'^leaders/(?P<realm>[a-zA-Z]+)/$', views.leaders, name='leaders'),
    url(r'^leaders/$', views.leaders, name='leaders_all'),
    url(r'^custom_leaders/$', views.leaders, name='custom_leaders'),
    url(r'^leaders_api/$', views.leaders_api, name='leaders_api'),
    url(r'^render_leaders/$', views.render_leaders, name='render'),
    url(r'^guilds/$', views.by_guild, name='guilds'),
    url(r'^charts/$', views.charts, name='charts'),
    url(r'^by_class/$', views.by_class, name='by_class'),
    url(r'^add_by_name/(?P<rawname>[a-zA-Z]+)/$', views.push_name, name='push_name'),
]
