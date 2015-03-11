from django.conf.urls import patterns, include, url
#from rest_framework.urlpatterns import format_suffix_patterns
from csrestapi import recommendations, autocomplete, training

from django.contrib import admin
admin.autodiscover()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^recommendation/(?P<action>[-\w]+)/$', recommendations.Recommendation.as_view()),
#    url(r'^recommendation/(?P<id>[0-9]+)/$', recommendations.Recommendation.as_view()),
    url(r'^autocomplete/(?P<action>[-\w]+)/$', autocomplete.Autocomplete.as_view()),
    url(r'^training/(?P<action>[-\w]+)/$', training.Training.as_view()),
)

#urlpatterns = format_suffix_patterns(urlpatterns)