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
    path('user/add/question', views.sign_up_with_no_registration_view, name='user-register-withnosignup'),
    path('user/actions/forgot-code', views.forgot_no_registration_code, name='user-actions-forgot-code'),
    path('user/delete/<int:id>/', views.delete_user, name='user-delete'),
    path('user/change-password/', views.change_password_view,
         name='user-change-password'),
     path('user/restore-password/', views.restore_password_view,
         name='user-restore-password'),
    # path('user/reset/', views.profile_view, name='user-reset-password'),
    # path('user/delete/', views.profile_view, name='user-delete'),
    path('user/forgot/', views.forgot_password_view, name='user-forgot-password'),
    path('user/send-link/', views.send_link, name='user-send-link'),
    path('user/activate/<int:uid>/<str:token>/',
         views.activate, name='user-activate'),
    path('user/change-email',
         views.change_email_view, name='user-change-email'),
    path('user/confirm-new-email/<int:uid>/<str:token>/<str:new_email>',
         views.confirm_new_email, name='user-confirm-new-email'),
    path('user/restore-password/<int:uid>/<str:token>/',
         views.restore_password, name='user-restore-password'),
    path('user/posts/<int:user_id>',
         views.my_posts_view, name='posts-get'), 

    # Post routes
    path('post/new', views.create_post, name='post-new'),
    path('post/new/anonymous', views.create_post_with_no_registration, name='post-new-withnoregistration'),
    path('post/details/<int:id>/<str:slug>',
         views.post_view, name='post-view'),
    path('post/edit/<int:id>/<str:slug>', views.post_edit, name='post-edit'),
    path('post/comment/<int:post_id>', views.add_comment, name='post-comment'),
    path('post/comment/vote/<int:comment_id>', views.comment_vote, name='post-comment-vote'),
    path('post/reply/<int:post_id>/<int:comment_id>',
         views.add_reply, name='post-reply'),
     path('user/comments/<int:user_id>',
         views.my_comments_view, name='comments-get'), 
     path('user/most-replied-comments/<int:user_id>',
         views.my_comments_most_replied_view, name='most-replied-comments'), 
     path('user/most-voted-comments/<int:user_id>',
         views.my_comments_most_voted_view, name='most-voted-comments'), 

    path('posts/latest', views.latest_posts, name='latest-posts'),
    path('posts/most-discussed', views.most_discussed_posts, name='most-discussed-posts'),
    path('posts/most-searched', views.most_searched_posts, name='most-searched-posts'),
    path('posts/with-latest-opinion-ordered', views.posts_with_latests_comment_order, name='with-latest-opinion-ordered'),
    path('posts/<str:category>', views.categorized_posts, name='filtered-posts'),
    # Messages routes
    path('user/messages/<int:user_id>', views.messages_view, name='messages'),
    path('user/messages/<int:user_id>/<int:message_id>', views.messages_view, name='get-message'),
    path('user/messages/new/<uuid:code>', views.new_message_view, name='new-message'),

    path('usage-terms/', views.privacy_policy_view, name='usage-terms'),
    path('about/', views.about_view, name='about'),
    path('about/users-ranking', views.users_ranking_view, name='users-ranking'),
    path('about/hjhjdhsfuhuehoksjjaskk41245452drvshvas66f62f6fal', views.last_activities_view, name='last_activities'),



]
