from raykomfi.models import Comment, User, Reply
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']

class LazyCommentsSerializer(serializers.ModelSerializer):
    page = serializers.CharField()
    csrfmiddlewaretoken = serializers.CharField()
    post_id = serializers.CharField()
    class Meta:
        model = Comment
        fields = ['post_id', 'page', 'csrfmiddlewaretoken']
        read_only_fields = ['post_id', 'page', 'csrfmiddlewaretoken']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Comment
        fields = ['user', 'votes']
        read_only_fields = ['user', 'votes']

class CommentAddSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField()
    class Meta:
        model = Comment
        fields = ['content', 'post_id']

class ReplyAddSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField()
    class Meta:
        model = Reply
        fields = ['content', 'comment_id']

class GetMessageSerializer(serializers.ModelSerializer):
    message_id = serializers.IntegerField()
    class Meta:
        model = Reply
        fields = ['message_id']