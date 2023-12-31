from django.db import models
from django.contrib.auth.models import User
import json
from django.utils import timezone
from django.db.models import F
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)

class CatPhoto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=200) 
    caption = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Thread(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    cat_photo = models.ForeignKey(CatPhoto, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    thread = models.ForeignKey(Thread, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_history = models.JSONField(default=list)  
    
    def add_to_edit_history(self, old_content):
        if self.content != old_content:  
            edited_at_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            edit_entry = {
                'content': old_content,
                'edited_at': edited_at_str
            }
            if edit_entry not in self.edited_history:
                self.edited_history = F('edited_history')
                self.save()

class Vote(models.Model):
    UPVOTE = 'up'
    DOWNVOTE = 'down'
    VOTE_CHOICES = [(UPVOTE, 'Upvote'), (DOWNVOTE, 'Downvote')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cat_photo = models.ForeignKey(CatPhoto, on_delete=models.CASCADE, null=True, blank=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True)
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
