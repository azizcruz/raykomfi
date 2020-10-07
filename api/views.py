from django.shortcuts import render
from raykomfi.models import Comment, User, Post

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import api.serializers as serializers
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader
from time import sleep

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
        sleep(2)
        return JsonResponse(output_data)

class BestUsers(APIView):
    '''
    List Top Users
    '''

    queryset = Comment.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        best_users = User.objects.all().annotate(Sum('my_comments__votes')).order_by('-my_comments__votes__sum').values('username', 'id', 'my_comments__votes__sum')
        return Response(best_users)