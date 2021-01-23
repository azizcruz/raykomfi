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
    viewer = serializers.CharField()
    class Meta:
        model = Comment
        fields = ['post_id', 'page', 'csrfmiddlewaretoken', 'user_id', 'viewer']
        read_only_fields = ['post_id', 'page', 'csrfmiddlewaretoken', 'user_id', 'viewer']

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

class NoRegisterCommentAddSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField()
    profile_image = serializers.CharField()
    class Meta:
        model = Comment
        fields = ['content', 'post_id', 'profile_image']

class NoRegisterCommentEditSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField()
    code = serializers.CharField()
    class Meta:
        model = Comment
        fields = ['content', 'comment_id', 'code']
    
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

class SearchBarSerializer(serializers.Serializer):
    searchField = serializers.CharField()
    users_posts = serializers.BooleanField()

    class Meta:
        fields = ['searchField', 'users_posts']

class SearchBarCommentsSerializer(serializers.Serializer):
    searchField = serializers.CharField()

    class Meta:
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

class SimilarQuestions(serializers.Serializer):
    category = serializers.CharField()
    class Meta:
        fields = ['category']

class FromYourCountryQuestions(serializers.Serializer):
    country = serializers.CharField()
    class Meta:
        fields = ['country']

class ContactUsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField()
    class Meta:
        fields = ['email', 'content']

