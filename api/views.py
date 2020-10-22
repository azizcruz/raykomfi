from django.shortcuts import render
from raykomfi.models import Comment, User, Post, Reply, Message

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import api.serializers as serializers
from django.db.models import Sum, Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.parsers import JSONParser
from django.template import loader
from time import sleep
from pdb import set_trace
from rest_framework import status
from notifications.signals import notify

class LazyPostsView(APIView):
    '''
    Lazy load more posts
    '''

    queryset = Post.objects.all()
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        page = request.POST.get('page')
        category = request.POST.get('category', '')
        posts = None
        if category != 'false':
            posts = Post.objects.prefetch_related('creator', 'category').filter(category__name__exact=category)
        else:
            posts = Post.objects.select_related('creator', 'category').all()
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
            comments = Comment.objects.prefetch_related('user' ,'replies').filter(post__id=serializer.data['post_id'])
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
                post = Post.objects.select_related('creator', 'category').filter(id__exact=serializer.data['post_id']).first()
                comment = Comment.objects.create(
                content=serializer.data['content'], user=request.user, post=post)
                comment = Comment.objects.select_related('user', 'post').filter(id=comment.id).first()
                referesh_post_view_html = loader.render_to_string(
                'referesh_post_view.html',
                {'post': comment.post, 'user': request.user})

                output_data = {
                    'view': referesh_post_view_html,
                    'message': 'success'
                }
                notify.send(request.user, recipient=post.creator , action_object=comment,  description=comment.get_noti_url(), target=comment, verb='comment')
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
                comment = Comment.objects.select_related('user', 'post').filter(id=serializer.data['comment_id']).first()
                reply = Reply.objects.create(content=serializer.data['content'], comment=comment, user=request.user)
                comment.replies.add(reply)
                comment.save()
                comment = Comment.objects.prefetch_related('user', 'post',
                'replies').filter(id__exact=serializer.data['comment_id']).first()
                referesh_comment_view_html = loader.render_to_string('referesh_comment_view.html', {'comment': comment, 'user': request.user})
                output_data = {
                    'view': referesh_comment_view_html,
                    'message': 'success'
                }
                notify.send(request.user, recipient=comment.user ,action_object=reply, description=reply.get_noti_url(), target=comment, verb='reply')
                return JsonResponse(output_data)
            except (Comment.DoesNotExist, Post.DoesNotExist):
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)

class LikeDislikeView(APIView):
    '''
    Add Reply
    '''
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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
                referesh_votes_view_html = loader.render_to_string('referesh_votes_view.html', {'comment': comment, 'user': request.user})
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

    def post(self, request):
        serializer = serializers.GetMessageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                fetched_message = Message.objects.select_related('user',
                'receiver').filter(id__exact=serializer.data['message_id']).first()
                fetched_message.is_read = True
                fetched_message.save()
                messages = Message.objects.select_related('user', 'receiver').filter(receiver__exact=request.user.id)
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

class SearchPostsView(APIView):
    '''
    Search Posts
    '''
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = serializers.SearchBarSerializer(data=request.data)
        if serializer.is_valid():
            q = serializer.data['searchField']
            posts = Post.objects.prefetch_related('creator', 'comments', 'category').filter(Q(title__icontains=q) | Q(content__icontains=q)).annotate(counted_comments=Sum('comments')).order_by('-counted_comments')
            referesh_posts_view_html = loader.render_to_string('posts.html', {'posts': posts, 'user': request.user})
            output_data = {
                'view': referesh_posts_view_html,
                'message': 'success'
            }

            if posts == []:
                return Response({'message': 'not found'}, status=status.HTTP_404_NOT_FOUND)

            return JsonResponse(output_data)
        