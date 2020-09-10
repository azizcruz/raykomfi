from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'raykomfi'

urlpatterns = [
    # User routes
    path('', views.index, name='raykomfi-home'),
    path('user/profile/<int:id>', views.profile_view, name='user-profile'),
    path('user/signin/', views.sign_in_view, name='user-signin'),
    path('user/signout/', views.user_logout, name='user-signout'),
    path('user/register/', views.sign_up_view, name='user-register'),
    path('user/change_password/', views.change_password_view,
         name='user-change-password'),
    # path('user/reset/', views.profile_view, name='user-reset-password'),
    # path('user/delete/', views.profile_view, name='user-delete'),
    path('user/forgot/', views.forgot_password_view, name='user-forgot-password'),
    path('user/activate/<uidb64>/<token>/',
         views.activate, name='user-activate'),

    # Post routes
    path('post/new', views.create_post, name='post-new'),
    # path('post/edit', views.profile_view, name='post-edit'),
    path('post/details/<int:id>', views.post_view, name='post-edit'),
    # path('post/delete', views.profile_view, name='post-edit'),
]
