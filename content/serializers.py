from rest_framework import serializers
from .models import Content, Comment

# Comment
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content_id', 'text']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['pk', 'content_id', 'commenter_id', 'text', 'created_at', 'updated_at']


# Content
class ContentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['title', 'text', 'image']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class ContentSerializer(serializers.ModelSerializer):
    # nested serializer # 게시글에 여러 개의 댓글을 포함한다.
    # Content의 정보를 전달할 때 연결된 comment의 전체 정보까지 함께 준다.
    include_comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = ['pk', 'writer_id', 'title', 'text', 'image', 'created_at', 'updated_at', 'include_comments']


