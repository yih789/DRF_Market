from django.db import models
from login.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.
class Content(models.Model):
    writer_id = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='contents') # 외래키
    title = models.CharField(max_length=50)
    text = models.TextField()
    image = models.ImageField(upload_to='content/contentImages/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    commenter_id = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='comments')  # 외래키
    content_id = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='include_comments')

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)