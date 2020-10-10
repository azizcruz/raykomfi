from raykomfi.models import Comment, User, Reply
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']

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
    post_id = serializers.IntegerField()
    class Meta:
        model = Reply
        fields = ['content', 'comment_id', 'post_id']