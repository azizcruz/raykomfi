from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views
import debug_toolbar


app_name = 'raykomfi'

urlpatterns = [
    # User routes
    path('', views.index, name='raykomfi-home'),
    path('user/profile/<int:id>/', views.profile_view, name='user-profile'),
    path('user/signin/', views.sign_in_view, name='user-signin'),
    path('user/signout/', views.user_logout, name='user-signout'),
    path('user/register/', views.sign_up_view, name='user-register'),
    path('user/delete/<int:id>/', views.delete_user, name='user-delete'),
    path('user/change-password/', views.change_password_view,
         name='user-change-password'),
     path('user/restore-password/', views.restore_password_view,
         name='user-restore-password'),
    # path('user/reset/', views.profile_view, name='user-reset-password'),
    # path('user/delete/', views.profile_view, name='user-delete'),
    path('user/forgot/', views.forgot_password_view, name='user-forgot-password'),
    path('user/send-link/', views.send_link, name='user-send-link'),
    path('user/activate/<uidb64>/<token>/',
         views.activate, name='user-activate'),
    path('user/restore-password/<uidb64>/<token>/',
         views.restore_password, name='user-restore-password'),

    # Post routes
    path('post/new', views.create_post, name='post-new'),
    path('post/details/<int:id>/<str:slug>',
         views.post_view, name='post-view'),
    path('post/edit/<int:id>/<str:slug>', views.post_edit, name='post-edit'),
    path('post/comment/<int:post_id>', views.add_comment, name='post-comment'),
    path('post/comment/vote/<int:comment_id>', views.comment_vote, name='post-comment-vote'),
    path('post/reply/<int:post_id>/<int:comment_id>',
         views.add_reply, name='post-reply'),
    path('posts/<int:user_id>',
         views.my_posts_view, name='posts-get'), 
    # path('post/delete', views.profile_view, name='post-delete'),

    # Messages routes
    path('user/messages/<int:user_id>', views.messages_view, name='messages'),
    path('user/messages/<int:user_id>/<int:message_id>', views.messages_view, name='get-message'),
    path('user/messages/new/<uuid:code>', views.new_message_view, name='new-message'),
]
