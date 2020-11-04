from raykomfi.models import Comment, User, Reply, Post, Report
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']

class LazyCommentsSerializer(serializers.ModelSerializer):
    page = serializers.CharField()
    csrfmiddlewaretoken = serializers.CharField()
    post_id = serializers.CharField()
    user_id = serializers.CharField()
    class Meta:
        model = Comment
        fields = ['post_id', 'page', 'csrfmiddlewaretoken', 'user_id']
        read_only_fields = ['post_id', 'page', 'csrfmiddlewaretoken', 'user_id']

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
    
class CommentEditSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField()
    class Meta:
        model = Comment
        fields = ['content', 'comment_id']

class ReplyAddSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField()
    class Meta:
        model = Reply
        fields = ['content', 'comment_id']

class ReplyEditSerializer(serializers.ModelSerializer):
    reply_id = serializers.IntegerField()
    comment_id = serializers.IntegerField()
    class Meta:
        model = Reply
        fields = ['content', 'reply_id', 'comment_id']

class GetMessageSerializer(serializers.ModelSerializer):
    message_id = serializers.IntegerField()
    class Meta:
        model = Reply
        fields = ['message_id']


class LikeDislikeSerializer(serializers.ModelSerializer):
    action_type = serializers.CharField()
    comment_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ['action_type', 'comment_id', 'user_id']

class SearchBarSerializer(serializers.ModelSerializer):
    searchField = serializers.CharField()

    class Meta:
        model = Post
        fields = ['searchField']

class UploadImageSerialzer(serializers.Serializer):
    image = serializers.ImageField()
    for_object = serializers.CharField(required=False)

    class Meta:
        fields = ['image', 'for_object']

class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = ['content', 'reported_url', 'topic']