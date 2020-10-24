from raykomfi import models
import api.views as views
from django.urls import include, path
from rest_framework import routers
from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

app_name = 'raykomfiapi'


urlpatterns = [
    path('best-users/', views.BestUsers.as_view()),
    path('lazy-posts/', views.LazyPostsView.as_view()),
    path('lazy-comments/', views.LazyCommentsView.as_view()),
    path('comment/add', views.CommentsView.as_view()),
    path('reply/add', views.RepliesView.as_view()),
    path('messages/get', views.GetMessageView.as_view()),
    path('comment/vote', views.LikeDislikeView.as_view()),
    path('posts/search', views.SearchPostsView.as_view()),
    path('post/image', views.UploadImageView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
