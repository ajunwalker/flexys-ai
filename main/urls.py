from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^project/(?P<id>[0-9a-zA-Z-]+)/$', views.index, name='index'),
    url('^column/(?P<id>[0-9a-zA-Z-]+)/$', views.GetColumnInfo.as_view(), name="column-info"),
    url('^projects/(?P<id>[0-9a-zA-Z-]+)/', views.GetProjectInfo.as_view(), name="project-info"),
    url('^model/(?P<id>[0-9a-zA-Z-]+)/$', views.GetModelInfo.as_view(), name="model-info"),
    path('', views.upload_view, name='upload_view'),
]
