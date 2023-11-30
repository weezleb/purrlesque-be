from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'catphotos', CatPhotoViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'threads', ThreadViewSet)

vote_list = VoteViewSet.as_view({
    'post': 'create_vote'
})

vote_detail = VoteViewSet.as_view({
    'delete': 'delete_vote'
})

vote_update = VoteViewSet.as_view({
    'put': 'update_vote'
})


urlpatterns = [
    path('', include(router.urls)),
    path('api/vote/', vote_list, name='vote-list'),
    path('api/vote/<int:pk>/', vote_detail, name='vote-detail'),
    path('api/vote/<int:pk>/update/', vote_update, name='update_vote'),
]