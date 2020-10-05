from django.shortcuts import render
from raykomfi.models import Comment, User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
import api.serializers as serializers
from django.db.models import Sum
from django.forms.models import model_to_dict

class BestUsers(APIView):
    '''
    List Top Users
    '''

    queryset = Comment.objects.all()

    def get(self, request, format=None):
        best_users = User.objects.all().annotate(Sum('my_comments__votes')).order_by('-my_comments__votes__sum').values('username', 'id', 'my_comments__votes__sum')
        return Response(best_users)