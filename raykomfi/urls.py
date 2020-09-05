from django.urls import path
from . import views

app_name = 'raykomfi'

urlpatterns = [
    path('', views.index, name='raykomfi-home'),
    path('user/profile/<int:id>', views.profile_view, name='user-profile'),
    path('user/signin/', views.sign_in_view, name='user-signin'),
    # path('user/signout/', views.profile_view, name='user-signout'),
    path('user/register/', views.sign_up_view, name='user-register'),
    path('user/change_password/', views.change_password_view,
         name='user-change-password'),
    # path('user/reset/', views.profile_view, name='user-reset-password'),
    # path('user/delete/', views.profile_view, name='user-delete'),
    path('user/forgot/', views.forgot_password_view, name='user-forgot-password'),

    # path('post/new', views.profile_view, name='post-new'),
    # path('post/edit', views.profile_view, name='post-edit'),
    # path('post/details', views.profile_view, name='post-edit'),
    # path('post/delete', views.profile_view, name='post-edit'),
]
