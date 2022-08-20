from django.urls import path
from . import views

urlpatterns = [
    path("contentCreate/", views.ContentCreateAPI.as_view(), name='create_content'),
    path("content/list/", views.ContentListAPI.as_view(), name='content_list'),
    path("content/<int:content_id>/", views.ContentAPI.as_view(), name='content'),
    path("comment/", views.CommentsAPI.as_view(), name='create_comment'),
    path("comment/<int:comment_id>/", views.CommentAPI.as_view(), name='comment'),
]


