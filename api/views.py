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
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit



class LazyPostsView(APIView):
    '''
    Lazy load more posts
    '''

    queryset = Post.objects.all()
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='100/m', block=True))
    def post(self, request, format=None):
        page = request.POST.get('page')
        category = request.POST.get('category', '')
        user_id = request.POST.get('user_id')
        posts = None
        if user_id != 'false':
            posts = Post.objects.prefetch_related('creator', 'category').filter(creator__id=int(user_id))
        elif category != 'false':
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
        data_to_render = {'posts': posts}
        if(user_id != 'false'):
            data_to_render['show_edit'] = True
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

    @method_decorator(ratelimit(key='ip', rate='100/m', block=True))
    def post(self, request, format=None):
        page = request.POST.get('page')
        serializer = serializers.LazyCommentsSerializer(data=request.data)
        if serializer.is_valid():
            comments = Comment.objects.prefetch_related('user' ,'replies').filter(post__id=serializer.data['post_id'])
            results_per_page = 10
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

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def get(self, request, format=None):
        best_users = User.objects.all().annotate(Sum('my_comments__votes')).order_by('-my_comments__votes__sum').values('username', 'id', 'my_comments__votes__sum')
        return Response(best_users)


class CommentsView(APIView):
    '''
    Add comment
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
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

    @method_decorator(ratelimit(key='ip', rate='3/m', block=True))
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
    Vote a comment
    '''
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
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

    @method_decorator(ratelimit(key='ip', rate='10/m', block=True))
    def post(self, request):
        serializer = serializers.SearchBarSerializer(data=request.data)
        if serializer.is_valid():
            q = serializer.data['searchField']
            posts = Post.objects.prefetch_related('creator', 'comments', 'category').filter(Q(title__icontains=q) | Q(content__icontains=q)).annotate(counted_comments=Sum('comments')).order_by('-counted_comments')
            referesh_posts_view_html = loader.render_to_string('posts.html', {'posts': posts, 'user': request.user, 'search_request': True})
            output_data = {
                'view': referesh_posts_view_html,
                'message': 'success'
            }

            if posts == []:
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
                set_trace()
                return blob.public_url
    