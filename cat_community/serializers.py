from rest_framework import serializers
from .models import UserProfile, CatPhoto, Comment, Thread, Vote

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'bio']

class CatPhotoSerializer(serializers.ModelSerializer):
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = CatPhoto
        fields = ['id', 'user', 'user_id', 'image_url', 'caption', 'uploaded_at', 'upvotes', 'downvotes']
        read_only_fields = ['user', 'user_id', 'image_url', 'upvotes', 'downvotes']

    def get_upvotes(self, obj):
        return obj.vote_set.filter(vote_type='up').count()

    def get_downvotes(self, obj):
        return obj.vote_set.filter(vote_type='down').count()



class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ['id', 'title', 'content', 'created_at', 'user']
        read_only_fields = ['user']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'cat_photo', 'thread', 'user', 'content', 'created_at']
        read_only_fields = ['user']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['user', 'cat_photo', 'thread', 'vote_type']
