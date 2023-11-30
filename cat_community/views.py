from .models import *
from .serializers import *
import boto3
from django.conf import settings
import uuid
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        if not username or not password or not email:
            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username, email, password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            is_admin = user.is_superuser
            return Response({
                'token': token.key, 
                'userId': user.id, 
                'isAdmin': is_admin
            })
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class CatPhotoViewSet(viewsets.ModelViewSet):
    queryset = CatPhoto.objects.all()
    serializer_class = CatPhotoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        queryset = CatPhoto.objects.all()
        sort = self.request.query_params.get('sort')
        if sort == 'popular':
            queryset = queryset.annotate(vote_count=Count('vote')).order_by('-vote_count')
        return queryset

    def perform_create(self, serializer):
        image = self.request.FILES.get('file')  
        if image:
            s3_client = boto3.client('s3', 
                                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
                                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            file_name = f"cat_photos/{uuid.uuid4().hex}_{image.name}"
            s3_client.upload_fileobj(image, settings.AWS_STORAGE_BUCKET_NAME, file_name)
            image_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
            serializer.save(image_url=image_url, user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        cat_photo = self.get_object()
        if request.user != cat_photo.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this photo.")
        return super(CatPhotoViewSet, self).destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        cat_photo = self.get_object()
        if request.user != cat_photo.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to edit this photo.")
        return super(CatPhotoViewSet, self).update(request, *args, **kwargs)

class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def destroy(self, request, *args, **kwargs):
        thread = self.get_object()
        if request.user != thread.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this thread.")
        return super(ThreadViewSet, self).destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        thread = self.get_object()
        if request.user != thread.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to edit this thread.")
        return super(ThreadViewSet, self).update(request, *args, **kwargs)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cat_photo_id = self.request.data.get('cat_photo')
        thread_id = self.request.data.get('thread')

        if cat_photo_id:
            cat_photo = get_object_or_404(CatPhoto, pk=cat_photo_id)
            serializer.save(user=self.request.user, cat_photo=cat_photo)
        elif thread_id:
            thread = get_object_or_404(Thread, pk=thread_id)
            serializer.save(user=self.request.user, thread=thread)
        else:
            raise ValidationError("A cat photo or thread must be provided.")

    def get_queryset(self):
        queryset = Comment.objects.all()
        cat_photo_id = self.request.query_params.get('cat_photo')
        thread_id = self.request.query_params.get('thread')

        if cat_photo_id:
            queryset = queryset.filter(cat_photo_id=cat_photo_id)
        elif thread_id:
            queryset = queryset.filter(thread_id=thread_id)

        return queryset
    
    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user != comment.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to edit this comment.")
        old_content = comment.content 
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200 and old_content != comment.content:
            comment.add_to_edit_history(old_content)
        return response

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user != comment.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this comment.")
        return super().destroy(request, *args, **kwargs)


class VoteViewSet(viewsets.ViewSet):

    def create_vote(self, request):
        user = request.user
        cat_photo_id = request.data.get('cat_photo')
        thread_id = request.data.get('thread')
        vote_type = request.data.get('vote_type')

        existing_vote = None
        if cat_photo_id:
            existing_vote = Vote.objects.filter(user=user, cat_photo_id=cat_photo_id).first()
        elif thread_id:
            existing_vote = Vote.objects.filter(user=user, thread_id=thread_id).first()

        if existing_vote:
            return Response({'error': 'You have already voted.'}, status=status.HTTP_400_BAD_REQUEST)

        vote = Vote(user=user, vote_type=vote_type)
        if cat_photo_id:
            vote.cat_photo_id = cat_photo_id
        elif thread_id:
            vote.thread_id = thread_id
        vote.save()

        return Response({'message': 'Vote recorded.'}, status=status.HTTP_201_CREATED)

    def delete_vote(self, request, pk=None):
        vote = get_object_or_404(Vote, pk=pk)
        if vote.user != request.user and not request.user.is_superuser:
            raise PermissionDenied("You cannot delete someone else's vote.")
        vote.delete()
        return Response({'message': 'Vote deleted.'}, status=status.HTTP_204_NO_CONTENT)

    def update_vote(self, request, pk=None):
        vote = get_object_or_404(Vote, pk=pk)
        if vote.user != request.user and not request.user.is_superuser:
            raise PermissionDenied("You cannot edit someone else's vote.")
        new_vote_type = request.data.get('vote_type')
        if new_vote_type not in [Vote.UPVOTE, Vote.DOWNVOTE]:
            return Response({'error': 'Invalid vote type.'}, status=status.HTTP_400_BAD_REQUEST)

        vote.vote_type = new_vote_type
        vote.save()

        return Response({'message': 'Vote updated.'}, status=status.HTTP_200_OK)

