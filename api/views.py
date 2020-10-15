from django.shortcuts import render
from raykomfi.models import Comment, User, Post, Reply, Message

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import api.serializers as serializers
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.parsers import JSONParser
from django.template import loader
from time import sleep
from pdb import set_trace
from rest_framework import status

class LazyPostsView(APIView):
    '''
    Lazy load more posts
    '''

    queryset = Post.objects.all()
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        page = request.POST.get('page')
        posts = Post.objects.all()
        # use Django's pagination
        # https://docs.djangoproject.com/en/dev/topics/pagination/
        results_per_page = 10
        paginator = Paginator(posts, results_per_page)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(2)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        # build a html posts list with the paginated posts
        posts_html = loader.render_to_string(
            'posts.html',
            {'posts': posts}
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

    def post(self, request, format=None):
        page = request.POST.get('page')
        serializer = serializers.LazyCommentsSerializer(data=request.data)
        if serializer.is_valid():
            comments = Comment.objects.prefetch_related('replies').filter(post__id=serializer.data['post_id'])
            results_per_page = 5
            paginator = Paginator(comments, results_per_page)
            try:
                comments = paginator.page(page)
            except PageNotAnInteger:
                comments = paginator.page(2)
            except EmptyPage:
                comments = paginator.page(paginator.num_pages)
            comments_html = loader.render_to_string(
                'comments.html',
                {'comments': comments, 'user': request.user}
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

    def get(self, request, format=None):
        best_users = User.objects.all().annotate(Sum('my_comments__votes')).order_by('-my_comments__votes__sum').values('username', 'id', 'my_comments__votes__sum')
        return Response(best_users)


class CommentsView(APIView):
    '''
    Add comment
    '''
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = serializers.CommentAddSerializer(data=request.data)
        if serializer.is_valid():
            try:
                post = Post.objects.prefetch_related(
                    'comments').prefetch_related('comments__replies').get(id__exact=serializer.data['post_id'])
                comment = Comment.objects.create(
                content=serializer.data['content'], user=request.user, post=post)
                comment = Comment.objects.get(id=comment.id)
                referesh_post_view_html = loader.render_to_string(
                'referesh_post_view.html',
                {'post': comment.post, 'user': request.user})

                output_data = {
                    'view': referesh_post_view_html,
                    'message': 'success'
                }

                return JsonResponse(output_data)
            except (Comment.DoesNotExist, Post.DoesNotExist):
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class RepliesView(APIView):
    '''
    Add Reply
    '''
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = serializers.ReplyAddSerializer(data=request.data)
        if serializer.is_valid():
            try:
                comment = Comment.objects.get(id=serializer.data['comment_id'])
                reply = Reply.objects.create(content=serializer.data['content'], comment=comment, user=request.user)
                comment.replies.add(reply)
                comment.save()
                comment = Comment.objects.prefetch_related(
                'replies').get(id__exact=serializer.data['comment_id'])
                referesh_comment_view_html = loader.render_to_string('referesh_comment_view.html', {'comment': comment, 'user': request.user})
                output_data = {
                    'view': referesh_comment_view_html,
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

    def post(self, request):
        serializer = serializers.GetMessageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                fetched_message = Message.objects.prefetch_related(
                'receiver').get(id__exact=serializer.data['message_id'])
                fetched_message.is_read = True
                fetched_message.save()
                messages = Message.objects.filter(receiver__exact=request.user.id)
                referesh_message_view_html = loader.render_to_string('messages.html', {'fetched_message': fetched_message, 'user': request.user, 'user_messages': messages})
                output_data = {
                    'view': referesh_message_view_html,
                    'message': 'success'
                }

                return JsonResponse(output_data)
            except Message.DoesNotExist:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)