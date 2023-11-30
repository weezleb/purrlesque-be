from django.contrib import admin
from .models import UserProfile, CatPhoto, Thread, Comment

admin.site.register(UserProfile)
admin.site.register(CatPhoto)
admin.site.register(Thread)
admin.site.register(Comment)
