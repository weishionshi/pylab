"""TestToolsCollection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from libManager import views

urlpatterns = [
    # url(r'^index/$', views.index),
    url(r'^addBook/$', views.add_book),
    url(r'^save/$', views.save)
    # url(r'^add/init/$', views.init),
    # url(r'^add/save/$', views.save),
    # url(r'^add/queryAll/$', views.query_all),
    # url(r'^add/$', views.add),
    # url(r'^add/update/$', views.update),
    # url('(?P<id_>[0-9]+)/delete/', views.delete)
]
