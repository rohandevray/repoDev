from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('',views.org_tree,name="index"),
    path('/<int:org_id>',views.orgdetail,name="orgDetail"),
]