from raykomfi import models
import api.views as views
from django.urls import include, path
from rest_framework import routers

urlpatterns = [
    path('best-users/', views.BestUsers.as_view()),
    path('lazy-posts/', views.LazyPostsView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
