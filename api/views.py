from django.shortcuts import render
from raykomfi.models import Comment, User, Post, Reply, Message, Report, NoRegistrationCode, Category, HomeAdMessages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import api.serializers as serializers
from django.db.models import Sum, Q, Max
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.parsers import JSONParser
from django.template import loader
from time import sleep
from pdb import set_trace
from rest_framework import status
from notifications.signals import notify
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
import datetime
from django.utils import timezone
from django.core.cache import cache
from notifications.signals import notify
from django.middleware.csrf import get_token
from raykomfi.background_tasks import send_notify
from notifications.models import Notification
from .models import BestUserListTrack
import json
from random import sample
from dotenv import load_dotenv
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from raykomfi.forms import get_random_image_path
load_dotenv()





class LazyPostsView(APIView):
    '''
    Lazy load more posts
    '''

    queryset = Post.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = ()

    @method_decorator(ratelimit(key='ip', rate='100/m', block=True))
    def post(self, request, format=None):
        page = request.POST.get('page')
        category = request.POST.get('category', '')
        user_id = request.POST.get('user_id')
        posts = None
        if user_id != 'false':
            posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(creator__id=int(user_id)).annotate(max_activity=Max('comments__created')).order_by('-max_activity')
        elif category != 'false':
            posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(category__name__exact=category, isActive=True).annotate(max_activity=Max('comments__created')).order_by('-max_activity')
        else:
            posts = Post.objects.prefetch_related('creator', 'category', 'comments').filter(isActive=True)
        # use Django's pagination
        # https://docs.djangoproject.com/en/dev/topics/pagination/
        results_per_page = 8
        paginator = Paginator(posts, results_per_page)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(2)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        # build a html posts list with the paginated posts
        data_to_render = {'posts': posts}
        if(user_id != 'false'):
            data_to_render['show_edit'] = True

        if user_id != 'false':
            csrf_token = get_token(request)
            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
            data_to_render['csrf_token'] = csrf_token
            posts_html = loader.render_to_string(
            'user_posts.html',
            data_to_render
        )
        elif category != 'false':
            posts_html = loader.render_to_string(
            'posts.html',
            data_to_render
        )
        else:
            posts_html = loader.render_to_string(
            'posts.html',
            data_to_render
        )    
        

        # package output data and return it as a JSON object
        output_data = {
            'posts_html': posts_html,
            'has_next': posts.has_next()
        }
        return JsonResponse(output_data)

class LazyCommentsView(APIView):
    '''
    Lazy load more comments
    '''

    queryset = Comment.objects.prefetch_related('comments__replies').all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = ()

    @method_decorator(ratelimit(key='ip', rate='100/m', block=True))
    def post(self, request, format=None):
        serializer = serializers.LazyCommentsSerializer(data=request.data)
        if serializer.is_valid():
            comments = []
            page = serializer.data['page']
            user_id = serializer.data['user_id']
            viewer = serializer.data['viewer']
            
            if viewer != 'false':
                request.user = User.objects.filter(id=viewer).first()
            if user_id != 'false':
                comments = Comment.objects.prefetch_related('user' ,'replies').filter(user__id=user_id)
            else:
                comments = Comment.objects.prefetch_related('user' ,'replies').filter(post__id=serializer.data['post_id'])
            results_per_page = 5
            paginator = Paginator(comments, results_per_page)
            try:
                comments = paginator.page(page)
            except PageNotAnInteger:
                comments = paginator.page(2)
            except EmptyPage:
                comments = paginator.page(paginator.num_pages)

            csrf_token = get_token(request)
            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)

            comments_html = None
            if user_id != 'false':
                comments_html = loader.render_to_string(
                'user_comments.html',
                {'comments': comments, 'user': request.user, 'csrf_token': csrf_token}
            )
            else:
                comments_html = loader.render_to_string(
                'comments.html',
                {'comments': comments, 'user': request.user, 'csrf_token': csrf_token}
            )
            output_data = {
                'comments_html': comments_html,
                'has_next': comments.has_next()
            }
            return JsonResponse(output_data)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class BestUsers(APIView):
    '''
    List Top Users
    '''

    queryset = Comment.objects.all()
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='30/m', block=True))
    def get(self, request, format=None):
        today_date = timezone.now()
        current_best_users = BestUserListTrack.objects.all().first()
        if current_best_users:
            current_best_users = json.loads(current_best_users.content)
            return Response(current_best_users['best_users'])
        else:
            if not current_best_users or datetime.datetime.today().day == 5 and current_best_users.created + datetime.timedelta(days=30) < today_date:
                anonymousUser = User.objects.filter(email='anonymous@anonymous.com').first()
                comment = Comment.objects.all().last() 
                best_users = User.objects.filter(
                    my_comments__created__lte=timezone.now()-datetime.timedelta(days=1),
                    my_comments__created__gt=timezone.now()-datetime.timedelta(days=30),
                    ).annotate(Sum('my_comments__votes')).order_by('-my_comments__votes__sum')[:10]

                users_list = {'best_users': [], 'last_time_checked': f"{today_date.day}-{today_date.month}-{today_date.year}"}
                obj = {}
                for rank, user in enumerate(best_users):
                    notify.send(anonymousUser, recipient=user , action_object=comment,  description='/', target=comment, verb='best_user')
                    if user.last_time_best_user == None or user.my_comments__votes__sum > 0.0:
                        if rank + 1 in [1, 2]:
                            if user.last_time_best_user == None or ((user.user_trust != 6.0 and user.user_trust > -1.0) and (user.last_time_best_user + datetime.timedelta(days=30) > today_date)):
                                if user.user_trust == 5.5:
                                    user.user_trust = 6.0
                                else:
                                    user.user_trust += 1.0
                                user.last_time_best_user = today_date
                        else:
                            if user.last_time_best_user == None or ((user.user_trust != 6.0 and user.user_trust > -1.0) and (user.last_time_best_user + datetime.timedelta(days=30) > today_date)):
                                user.user_trust += 0.5
                                user.last_time_best_user = today_date
                        user.save()
                        obj['username'] = user.username
                        obj['id'] = user.id
                        obj['my_comments__votes__sum'] = user.my_comments__votes__sum
                        users_list['best_users'].append(obj)
                        obj = {}
                BestUserListTrack.objects.create(content=json.dumps(users_list))
                return Response(users_list['best_users'])
            else:
                return Response({'last_time_checked': '', 'best_users': []})


class NoRegisterCommentsView(APIView):
    '''
    Add no register comment
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='2/m', block=True))
    def post(self, request):
        serializer = serializers.NoRegisterCommentAddSerializer(data=request.data)
        if serializer.is_valid():
            post = Post.objects.select_related('creator', 'category').filter(id__exact=serializer.data['post_id']).first()
            
            if post:
                comment = Comment.objects.create(
                content=serializer.data['content'], user=None, post=post, user_image=serializer.data['profile_image'])
                comment = Comment.objects.select_related('user', 'post').filter(id=comment.id).first()
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_post_view_html = loader.render_to_string(
                'referesh_post_view.html',
                {'post': comment.post, 'user': None, 'csrf_token': csrf_token})

                output_data = {
                    'view': referesh_post_view_html,
                    'message': 'success',
                    'comment_id': comment.id
                }
                anonymousUser = User.objects.filter(email='anonymous@anonymous.com').first()
                if post.creator == None:
                    post.creator = anonymousUser
                if request.user.id != post.creator.id and post.creator.get_notifications == True:
                    notify.send(anonymousUser, recipient=post.creator , action_object=comment,  description=comment.get_noti_url(), target=post, verb='comment')
                return JsonResponse(output_data)
            else:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(ratelimit(key='ip', rate='2/m', block=True))
    def put(self, request):
        serializer = serializers.NoRegisterCommentEditSerializer(data=request.data)
        if serializer.is_valid():
            comment = Comment.objects.select_related('user').filter(id__exact=serializer.data['comment_id'])
            if comment:
                comment.update(content=serializer.data['content'])
                comment = Comment.objects.select_related('user', 'post').filter(id=comment[0].id).first()
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_comment_view_html = loader.render_to_string(
                'referesh_comment_view.html',
                {'comment': comment, 'user': None, 'csrf_token': csrf_token})

                output_data = {
                    'view': referesh_comment_view_html,
                    'message': 'success'
                }
                return JsonResponse(output_data)
            else:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class CommentsView(APIView):
    '''
    Add comment
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
    def post(self, request):
        # if request.user.email_active == False:
        #     return Response({'message': 'account not activated'}, status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.CommentAddSerializer(data=request.data)
        if serializer.is_valid():
            post = Post.objects.select_related('creator', 'category').filter(id__exact=serializer.data['post_id']).first()
            if post:
                comment = Comment.objects.create(
                content=serializer.data['content'], user=request.user, post=post)
                comment = Comment.objects.select_related('user', 'post').filter(id=comment.id).first()
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_post_view_html = loader.render_to_string(
                'referesh_post_view.html',
                {'post': comment.post, 'user': request.user, 'csrf_token': csrf_token})

                output_data = {
                    'view': referesh_post_view_html,
                    'message': 'success',
                    'comment_id': comment.id
                }
                anonymousUser = User.objects.filter(email='anonymous@anonymous.com').first()
                if post.creator == None:
                    post.creator = anonymousUser
                if post.creator and request.user.id != post.creator.id and post.creator.get_notifications == True:
                    notify.send(request.user, recipient=post.creator , action_object=comment,  description=comment.get_noti_url(), target=post, verb='comment')
                return JsonResponse(output_data)
            else:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
    def put(self, request):
        serializer = serializers.CommentEditSerializer(data=request.data)
        if serializer.is_valid():
            comment = Comment.objects.select_related('user').filter(id__exact=serializer.data['comment_id'])
            if comment:
                comment.update(content=serializer.data['content'])
                comment = Comment.objects.select_related('user', 'post').filter(id=comment[0].id).first()
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_comment_view_html = loader.render_to_string(
                'referesh_comment_view.html',
                {'comment': comment, 'user': request.user, 'csrf_token': csrf_token})

                output_data = {
                    'view': referesh_comment_view_html,
                    'message': 'success'
                }
                return JsonResponse(output_data)
            else:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class RepliesView(APIView):
    '''
    Add Reply
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
    def post(self, request):
        # if request.user.email_active == False:
        #     return Response({'message': 'account not activated'}, status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.ReplyAddSerializer(data=request.data)
        if serializer.is_valid():
            comment = Comment.objects.select_related('user', 'post').filter(id=serializer.data['comment_id']).first()
            if comment:
                reply = Reply.objects.create(content=serializer.data['content'], comment=comment, user=request.user)
                comment.replies.add(reply)
                comment.save()
                comment = Comment.objects.prefetch_related('user', 'post',
                'replies').filter(id__exact=serializer.data['comment_id']).first()
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_comment_view_html = loader.render_to_string('referesh_comment_view.html', {'comment': comment, 'user': request.user, 'csrf_token': csrf_token})
                output_data = {
                    'view': referesh_comment_view_html,
                    'message': 'success'
                }

                anonymousUser = User.objects.filter(email='anonymous@anonymous.com').first()
                if comment.user == None:
                    comment.user = anonymousUser

                if request.user.id != comment.user.id and reply.user.get_notifications == True:
                    notify.send(request.user, recipient=comment.user ,action_object=reply, description=reply.get_noti_url(), target=comment, verb='reply')
                return JsonResponse(output_data)
            else:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)                
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
    def put(self, request):
        serializer = serializers.ReplyEditSerializer(data=request.data)
        if serializer.is_valid():
            reply = Reply.objects.select_related('user', 'comment').filter(id=serializer.data['reply_id'])
            if reply:
                reply.update(content=serializer.data['content'])
                comment = Comment.objects.prefetch_related('user', 'post',
                'replies').filter(id__exact=serializer.data['comment_id']).first()
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_comment_view_html = loader.render_to_string('referesh_comment_view.html', {'comment': comment, 'user': request.user, 'csrf_token': csrf_token})
                output_data = {
                    'view': referesh_comment_view_html,
                    'message': 'success'
                }
                return JsonResponse(output_data)
            else:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)   
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class AnonymousRepliesView(APIView):
    '''
    Add Reply As Anonymous
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='2/m', block=True))
    def post(self, request):
        serializer = serializers.ReplyAddSerializer(data=request.data)
        if serializer.is_valid():
            comment = Comment.objects.select_related('user', 'post').filter(id=serializer.data['comment_id']).first()
            if comment:
                anonymousUser = User.objects.filter(email='anonymous@anonymous.com').first()
                
                reply = Reply.objects.create(content=serializer.data['content'], comment=comment, user=anonymousUser, user_image=get_random_image_path())
                comment.replies.add(reply)
                comment.save()
                comment = Comment.objects.prefetch_related('user', 'post',
                'replies').filter(id__exact=serializer.data['comment_id']).first()
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_comment_view_html = loader.render_to_string('referesh_comment_view.html', {'comment': comment, 'user': request.user, 'csrf_token': csrf_token})
                output_data = {
                    'view': referesh_comment_view_html,
                    'message': 'success'
                }

                if comment.user != None and comment.user.email != 'anonymous@anonymous.com' and request.user.id != comment.user.id and comment.user.get_notifications == True:
                    notify.send(anonymousUser, recipient=comment.user ,action_object=reply, description=reply.get_noti_url(), target=comment, verb='reply')
                return JsonResponse(output_data)
            else:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)                
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)



class LikeDislikeView(APIView):
    '''
    Vote a comment
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        if request.user.email_active == False:
            return Response({'message': 'account not activated'}, status=status.HTTP_403_FORBIDDEN)
        serializer = serializers.LikeDislikeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                comment = Comment.objects.prefetch_related('user', 'voted_like', 'voted_dislike', 'post').filter(id=serializer.data['comment_id']).first()
                vote_type = serializer.data['action_type']
                if vote_type == 'like':
                    if request.user not in comment.voted_like.all() and request.user in comment.voted_dislike.all():
                        comment.voted_dislike.remove(request.user)
                        comment.voted_like.add(request.user)
                    else:
                        comment.voted_like.add(request.user)
                
                if vote_type == 'dislike':
                    if request.user not in comment.voted_dislike.all() and request.user in comment.voted_like.all():
                        comment.voted_dislike.add(request.user)
                        comment.voted_like.remove(request.user)
                    else:
                        comment.voted_dislike.add(request.user)

                comment.votes = comment.voted_like.all().count() - comment.voted_dislike.all().count()
                comment.save()
                comment = Comment.objects.prefetch_related('voted_like', 'voted_dislike').get(id=serializer.data['comment_id'])
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_votes_view_html = loader.render_to_string('referesh_votes_view.html', {'comment': comment, 'user': request.user, 'csrf_token': csrf_token})
                output_data = {
                    'view': referesh_votes_view_html,
                    'message': 'success'
                }

                return JsonResponse(output_data)
            except (Comment.DoesNotExist, Post.DoesNotExist):
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class GetMessageView(APIView):
    '''
    Get Message
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        if request.user.email_active == False:
            return Response({'message': 'account not activated'}, status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.GetMessageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                fetched_message = Message.objects.select_related('user',
                'receiver').filter(id__exact=serializer.data['message_id']).first()
                fetched_message.is_read = True
                fetched_message.save()
                messages = Message.objects.select_related('user', 'receiver').filter(receiver__exact=request.user.id)
                csrf_token = get_token(request)
                csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
                referesh_message_view_html = loader.render_to_string('messages.html', {'fetched_message': fetched_message, 'user': request.user, 'user_messages': messages, 'csrf_token': csrf_token})
                output_data = {
                    'view': referesh_message_view_html,
                    'message': 'success'
                }

                return JsonResponse(output_data)
            except Message.DoesNotExist:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class SearchPostsView(APIView):
    '''
    Search Posts
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        serializer = serializers.SearchBarSerializer(data=request.data)
        if serializer.is_valid():
            q = serializer.data['searchField']
            is_users_posts = serializer.data['users_posts']
            if q == '':
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

            if is_users_posts == True:
                posts = Post.objects.prefetch_related('creator', 'comments', 'category').filter(Q(title__icontains=q) | Q(content__icontains=q)).filter(creator__email=request.user.email).annotate(counted_comments=Sum('comments')).order_by('-counted_comments')
            else:
                posts = Post.objects.prefetch_related('creator', 'comments', 'category').filter(Q(title__icontains=q) | Q(content__icontains=q)).annotate(counted_comments=Sum('comments')).filter(isActive=True).order_by('-counted_comments')
            
            csrf_token = get_token(request)
            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)

            if is_users_posts == True:
                referesh_posts_view_html = loader.render_to_string('user_posts.html', {'posts': posts, 'user': request.user, 'search_request': True})
            else:
                referesh_posts_view_html = loader.render_to_string('posts.html', {'posts': posts, 'user': request.user, 'search_request': True, 'csrf_token': csrf_token})


            output_data = {
                'view': referesh_posts_view_html,
                'message': 'success'
            }

            if posts == []:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse(output_data)
        else:
            csrf_token = get_token(request)
            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
            if  request.data['users_posts'] == True:
                posts = Post.objects.prefetch_related('creator', 'comments', 'category').filter(creator__email=request.user.email).annotate(counted_comments=Sum('comments')).order_by('-counted_comments')
                referesh_posts_view_html = loader.render_to_string('user_posts.html', {'posts': posts, 'user': request.user, 'search_request': True, 'csrf_token': csrf_token})

            else:
                posts = Post.objects.prefetch_related('creator', 'comments', 'category').annotate(counted_comments=Sum('comments')).order_by('-counted_comments')
                referesh_posts_view_html = loader.render_to_string('posts.html', {'posts': posts, 'user': request.user, 'search_request': True, 'csrf_token': csrf_token})

            output_data = {
                'view': referesh_posts_view_html,
                'message': 'success'
            }

            if posts == []:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse(output_data)


class SearchCommentsView(APIView):
    '''
    Search Comments
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        serializer = serializers.SearchBarCommentsSerializer(data=request.data)
        if serializer.is_valid():
            q = serializer.data['searchField']
            comments = Comment.objects.prefetch_related('user', 'replies').filter(content__icontains=q, user__email=request.user.email)
            csrf_token = get_token(request)
            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
            referesh_user_comments_view_html = loader.render_to_string('user_comments.html', {'comments': comments, 'user': request.user, 'search_request': True, 'csrf_token': csrf_token})
            output_data = {
                'view': referesh_user_comments_view_html,
                'message': 'success'
            }

            if comments == []:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse(output_data)
        
        else:
            comments = Comment.objects.prefetch_related('user', 'replies').filter(user__email=request.user.email).annotate(counted_replies=Sum('replies')).order_by('-counted_replies')
            csrf_token = get_token(request)
            csrf_token_html = '<input type="hidden" name="csrfmiddlewaretoken" value="{}" />'.format(csrf_token)
            referesh_user_comments_view_html = loader.render_to_string('user_comments.html', {'comments': comments, 'user': request.user, 'search_request': True, 'csrf_token': csrf_token})
            output_data = {
                'view': referesh_user_comments_view_html,
                'message': 'success'
            }

            if comments == []:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse(output_data)

        
class UploadImageView(APIView):
    '''
    Search Posts
    '''

    permissions_classes = [permissions.IsAuthenticated]
    # parser_classes = (FileUploadParser,)

    def post(self, request):
        serializer = serializers.UploadImageSerialzer(data=request.data)
        serializer.initial_data['image'] = request.data['image']
        if serializer.is_valid():
            image = request.data['image']
            ALLOWED_TYPES =['image/jpg', 'image/png', 'image/jpeg']
            if image.content_type not in ALLOWED_TYPES:
                return Response({'message': 'invalid type'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                credentials_dict = {
                    'type': 'service_account',
                    'client_id': '106574927547522144622',
                    'client_email': 'raykomfi@raykomfi-1602072427110.iam.gserviceaccount.com',
                    'private_key_id': '25c2fc3760feefe98c99b613567eb9872bb2d9db',
                    'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCYWz35tuNd3fEP\nBxReaW53xyKGSt9p+H38miWP3MDhuZ1kGx9B2FBPQitv5BZVCLXjX5UvmxH8I+3K\nCnXh7BaCxIBdHdyUoi7hLpYdIQvm4dWvgcwhVl9bHloLGxhndU0YHFRMR4zeDUjZ\ni2ezhyjmXXn4eIQXwD2voGRvBT0UZIaZ2RIDHhx/5Xlak0eAoI/4V7kxNh450eXV\nExXcKsE7G/Vm27mCvw3WIWDAWMmdH1pzdLrJ2RbHCZxyQ5UoyN0NEAkXKmHElhxL\nliaJX1VxmcR56F+YaNp+xa78KRPxdVaa9p+3FEe0lC41RF2aeYD55HIbTWcgLFPF\n+4QeG14tAgMBAAECggEAHgWyzXucy7ExsJKmUKFpf4hZ1Qk5g64QE4ADoVjwmDpl\nmaWfj+/SiX/CQ/r37Js6DltWMEqYLW2eDLdpedK2L+ANZGv/PLnFz6FIuuY5bG55\nl2tWIIae5TtypmgZM7/haHwin2JlD5eiEJ5AGdgrNtPaNlx3OR/sd+h9CgSH//Wu\nUeTiKN564PwvKCffznvjG560mkMZaXDZL5Xruaz0cyMrwl3LO0QxlOQeFrbLvTHP\nKvnGMVTj2COGJikHb9ZRf3uJKCc5PyZ6MDPYS/U1SmLhCsL3AFaAD5ViiHxoebJ8\nrkqCF7tXq/sluhoUixSK2ORuesAtVqtnezDuPf+dUQKBgQDL27+svfelXyQkZ3Kv\nwzLfhh2oeq3oPgbZPPz5JDvZhvuQDLn4C6b8nGz1NbZdbEIETTax7hiqatm/WbHR\ndEUDV48YHmQpi5cIHmAqG1TaDDuy2m/riDGwAR+my1ktHXATCzcd+vjQCaH5fafZ\nekY0CxspwsTVWDDUe9sMp5I0vQKBgQC/Uz5wWeW0FGEgsHtHb0CcGkaMpb9zCGkL\n4btdroTGXosELHksahYsGAlK/Y5WfByrQk7XWmjTniz0MO7w3BoCKXK3Kfo+Bfy6\nX+NMks1/E4PA/+8yvswULumU7A/bSgIYOk1Nr0DZx9JuLeoPoeLZnQaEwgnjbjLt\n71+mJxe+MQKBgQCOkg8JNopdw545P4f72F5Z6SgQzkuV4ttTTs31SBv7U+XXpq7h\nBPUyMgwZqgjyaWX6MC4SXlwtwzCqHIa538DsR24yBf8y9wcXjHbgu+Cp5mhR+2bO\nqJ9nYkHKmuixHqdlCjDv7LfadwIqxHCBLnyupR3IJQkX0+fCkyRtQzyDWQKBgFxz\n6Gc4ObS0aF74iQny68DDPbY3XfVDaieQtA7IB2coRnsE1qUsunwiPVNchUyretsT\nFrAgAynHdKengb8oTPUgfEugYElacU7KiTb2dZDjqDY6NqdJ5aoXJU6OZ/cqoyp7\n+eEBQBA87CXL0CAvtUQ9CepbLZYWKUwq8QiEOYfxAoGBAL8pmwYg989ELoJkvNWI\nnmLiZIdQarLkaxUOWKfCq2RNNvZpmp2FvJJY67DlRkhhhnIi0nMh2Ec+yyRHV8AN\njfLXp0Paotr4O5Z8g0wURWizf7YqGepRtW2ZGfit6F3t04kOHewQ9x4ktCWgp1gv\ncf2eKBh/QkFFA+bEeBi250+S\n-----END PRIVATE KEY-----\n',
                }

                credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    credentials_dict
                )

                client = storage.Client(credentials=credentials, project='myproject')
                bucket = client.get_bucket('raykomfi')
                gdir = f'post_image/{image.name}'
                blob = bucket.blob(gdir)
                blob.upload_from_string(image.read(), content_type=image.content_type)
                return blob.public_url
    

class ReportView(APIView):
    '''
    Report View
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def post(self, request):
        serializer = serializers.ReportSerializer(data=request.data)
        if serializer.is_valid():
            admin = User.objects.get(email=os.getenv('ADMIN_EMAIL'))
            report = Report.objects.create(user=request.user, content=serializer.validated_data['content'], topic=serializer.validated_data['topic'], reported_url=serializer.validated_data['reported_url'])
            notify.send(request.user, recipient=admin ,action_object=report, description=serializer.validated_data['reported_url'] + '&read=1', target=report, verb='report')
            return JsonResponse({'message': 'تم الإبلاغ'})


class NotificationView(APIView):
    '''
    Notification View
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def delete(self, request):
        Notification.objects.filter(recipient=request.user).delete()
        return JsonResponse({'message': 'تم الحذف'})


class UserActivityView(APIView):
    '''
    User Activity View
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def put(self, request):
        User.objects.filter(id=request.user.id).update(latest_activity=timezone.now() + datetime.timedelta(minutes=2))
        return JsonResponse({'message': 'تم التحديث'})


class AdminActionsView(APIView):
    '''
    User Activity View
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='5/m', block=True))
    def post(self, request):
        if request.user.is_staff:
            request_type = request.data.get('type', '')
            action = request.data.get('action', '')
            url = request.data.get('url', '')
            id = int(request.data.get('id', ''))
            if request_type == 'post':
                post = Post.objects.filter(id=id).first()
                if post:
                    if action == 'delete':
                        post.delete()
                        return JsonResponse({'message': 'تم الحذف'})
                    if action == 'activate':
                        post.isActive = True
                        post.save()
                        return JsonResponse({'message': 'تم التفعيل'})
                    if action == 'deactivate':
                        post.isActive = False
                        post.save()
                        return JsonResponse({'message': 'تم الغاء التفعيل'})
                    if action == 'reportAsNotAllowed':
                        admin = User.objects.filter(email='support@raykomfi.com').first()
                        message = Message.objects.create(user=admin, receiver=post.creator, title="رسالة من إدارة رايكم في", content=f'<p>إستفسارك <a href={post.get_noti_url()}>{post.title}</a> مخالف لشروط إستخدام منصة رايكم في, سيتم حذف إستفسارك<p>')
                        notify.send(admin, recipient=post.creator ,action_object=post, description=message.get_noti_url(), target=post, verb='message')
                        return JsonResponse({'message': 'تم الإبلاغ'})

            if request_type == 'comment':
                comment = Comment.objects.filter(id=id).first()
                if comment:
                    if action == 'delete':
                        Notification.objects.filter(description=comment.get_noti_url()).delete()
                        comment.delete()
                        return JsonResponse({'message': 'تم الحذف'})
                    if action == 'reportAsNotAllowed':
                        admin = User.objects.filter(email='support@raykomfi.com').first()
                        message = Message.objects.create(user=admin, receiver=comment.user, title="رسالة من إدارة رايكم في", content=f"<p>رأيك <a href={comment.get_noti_url()}>{comment.content[0:20]}...</a> مخالف لشروط إستخدام منصة رايكم في, سيتم حذف رأيك<p>")
                        notify.send(admin, recipient=comment.user ,action_object=comment, description=message.get_noti_url(), target=comment, verb='message')
                        return JsonResponse({'message': 'تم الإبلاغ'})

            if request_type == 'reply':
                reply = Reply.objects.filter(id=id).first()
                if reply:
                    if action == 'delete':
                        Notification.objects.filter(description=reply.get_noti_url()).delete()
                        reply.delete()
                        return JsonResponse({'message': 'تم الحذف'})
                    if action == 'reportAsNotAllowed':
                        admin = User.objects.filter(email='support@raykomfi.com').first()
                        message = Message.objects.create(user=admin, receiver=reply.user, title="رسالة من إدارة رايكم في", content=f"<p>ردك <a href={reply.get_noti_url()}>{reply.content[0:20]}...</a> مخالف لشروط إستخدام منصة رايكم في, سيتم حذف ردك<p>")
                        notify.send(admin, recipient=reply.user ,action_object=reply, description=message.get_noti_url(), target=reply, verb='message')
                        return JsonResponse({'message': 'تم الإبلاغ'})
                else:
                    return JsonResponse({'message': 'لا يوجد'})
            else:
                return JsonResponse({'message': 'غير مخول لعمل هذا الشيء'}, status=status.HTTP_403_FORBIDDEN)

        else:
            return JsonResponse({'message': 'غير مخول لعمل هذا الشيء'}, status=status.HTTP_403_FORBIDDEN)




class LatestComments(APIView):
    '''
    Latest Comments
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='15/m', block=True))
    def get(self, request):
        latest_comments = Comment.objects.prefetch_related('user', 'post', 'replies').filter(post__isActive=True).order_by('-created')[:10]
        referesh_posts_view_html = loader.render_to_string('latest_comments.html', {'latest_comments': latest_comments})
        output_data = {
            'view': referesh_posts_view_html,
            'message': 'success'
        }
        return Response(output_data)

class SimilarQuestions(APIView):
    '''
    Similar Questions
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='15/m', block=True))
    def post(self, request):
        serializer = serializers.SimilarQuestions(data=request.data)

        if serializer.is_valid():
            rand_ids = Post.objects.select_related('creator', 'category').filter(category__name=serializer.data['category']).values_list('id', flat=True)
            related_posts = []
            if len(rand_ids) > 6:
                rand_ids = list(rand_ids)
                rand_ids = sample(rand_ids, 6)
                related_posts = Post.objects.select_related('creator', 'category').filter(id__in=rand_ids)

                referesh_posts_view_html = loader.render_to_string('similar_questions.html', {'related_posts': related_posts})

                output_data = {
                    'view': referesh_posts_view_html,
                    'message': 'success'
                }

                return Response(output_data)

            return JsonResponse({'message': 'not enough'})
            
        else:
            return JsonResponse({'message': 'غير مخول لعمل هذا الشيء'}, status=status.HTTP_403_FORBIDDEN)


class QuestionsNearYou(APIView):
    '''
    Post From Country
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='15/m', block=True))
    def post(self, request):
        serializer = serializers.FromYourCountryQuestions(data=request.data)

        if serializer.is_valid():
            rand_ids = Post.objects.select_related('creator', 'category').filter(creator__country__icontains=serializer.data['country']).values_list('id', flat=True)
            related_posts = []
                        
            if len(rand_ids) > 5:
                rand_ids = list(rand_ids)
                rand_ids = sample(rand_ids, 5)
                related_posts = Post.objects.select_related('creator', 'category').filter(id__in=rand_ids)

                referesh_posts_view_html = loader.render_to_string('similar_questions.html', {'related_posts': related_posts})
                
                output_data = {
                    'view': referesh_posts_view_html,
                    'message': 'success'
                }

                return Response(output_data)

            return JsonResponse({'message': 'not enough'})
            
        else:
            return JsonResponse({'message': 'غير مخول لعمل هذا الشيء'}, status=status.HTTP_403_FORBIDDEN)

class Categories(APIView):
    '''
    Categories
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='20/m', block=True))
    def get(self, request):
        categories = Category.objects.all()

        if categories:
            referesh_category_view_html = loader.render_to_string('categories.html', {'categories': categories})
                    
            output_data = {
                'view': referesh_category_view_html,
                'message': 'success'
            }

            return Response(output_data)

        else:
            return JsonResponse({'message': 'غير مخول لعمل هذا الشيء'}, status=status.HTTP_403_FORBIDDEN)

class AdMessages(APIView):
    '''
    Ad Messages
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='20/m', block=True))
    def get(self, request):
        messages = HomeAdMessages.objects.all()

        if messages:
            referesh_messages_view_html = loader.render_to_string('ad_messages.html', {'messages': messages})
                    
            output_data = {
                'view': referesh_messages_view_html,
                'message': 'success'
            }

            return Response(output_data)

        else:
            return JsonResponse({'message': 'غير مخول لعمل هذا الشيء'}, status=status.HTTP_403_FORBIDDEN)


class ContactUsView(APIView):
    '''
    Contact Us
    '''
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='2/m', block=True))
    def post(self, request):
        serializer = serializers.ContactUsSerializer(data=request.data)

        if serializer.is_valid():
            from_email = serializer.data['email']
            to_email = 'support@raykomfi.com'
            if len(serializer.data['email']) > 5:
                mail_subject = serializer.data['content'][:4]
            else:
                mail_subject = serializer.data['content']

            msg = EmailMultiAlternatives(
            f"{mail_subject}", "nothing", to=[to_email])
            template="email_content.html"
            html_email_template = get_template(template).render(
                {
                    'content': serializer.data['content'],
                    'email': from_email
                }
            )
            msg.attach_alternative(html_email_template, "text/html")
            msg.send()
            return Response({'message': 'تم إرسال رسالتك'})

        else:
            return JsonResponse({'message': 'خطأ من العميل'}, status=status.HTTP_400_FORBIDDEN)