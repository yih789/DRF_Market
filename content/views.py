from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

# model, serializer
from content.serializers import ContentSerializer, ContentCreateSerializer, CommentSerializer, CommentCreateSerializer
from content.models import Content, Comment, User

# swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Filter기능
#from django_filters.rest_framework import DjangoFilterBackend

# 필터링
from .pagination import PaginationHandlerMixin, ContentsPagination

# 로거 사용
import logging
logger = logging.getLogger('mylogger')  # 해당 이름의 로거를 불러온다.

# 공통 영역
from common.common import CommonView

from .permissions import ContentPermission, CommentPermission


# Content CREATE
class ContentCreateAPI(CommonView):
    def post(self, request):  # CREATE
        user = get_object_or_404(User, pk=self.user_id)
        serializer = ContentCreateSerializer(data=request.data)  # request
        if serializer.is_valid():
            serializer.save(writer_id=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # response


# Content READ_LIST => list, filter_list
# Pagination
class ContentListAPI(APIView, PaginationHandlerMixin):
    pagination_class = ContentsPagination
    serializer_class = ContentSerializer
    # READ list
    def get(self, request, format=None, *args, **kwargs):
        instance = Content.objects.all()
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                                                                           many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # READ filter_list
    def post(self, request, format=None, *args, **kwargs):
        word = request.POST['word']

        instance = Content.objects.filter(title__icontains=word) | Content.objects.filter(
            text__icontains=word) | Content.objects.filter(writer_id__username__icontains=word)

        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page,
                                                                           many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Content: pk 필요 => UPDATE, DELETE, RETRIEVE
class ContentAPI(APIView):
    permission_classes = [ContentPermission]


    # READ RETRIEVE
    def get(self, request, content_id):

        content = get_object_or_404(Content, id=content_id)
        serializer = ContentSerializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # UPDATE
    def put(self, request, content_id):
        content = get_object_or_404(Content, id=content_id)
        serializer = ContentCreateSerializer(content, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    def delete(self, request, content_id):
        content = get_object_or_404(Content, id=content_id)
        content.delete()  # 삭제
        return Response({"massage": "success delete"}, status=status.HTTP_200_OK)


# Comment: pk 필요 x
class CommentsAPI(CommonView):
    # CREATE
    def post(self, request):  # CREATE
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, pk=self.user_id)
            serializer.save(commenter_id=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"massage": "error"}, status=status.HTTP_400_BAD_REQUEST)

# Comment: pk 필요
class CommentAPI(APIView):
    permission_classes = [CommentPermission]
    '''
    def get_queryset(self):
        # all(), 모든 데이터를 갖고 오겠다
        return Comment.objects.all()
    '''
    def get_object(self, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        self.check_object_permissions(self.request, comment)
        return comment

    # UPDATE
    def put(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.text = request.data.get('text', comment.text)
        comment.save()
        serializer = CommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE
    def delete(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.delete()  # 삭제
        return Response({"massage": "success delete"}, status=status.HTTP_200_OK)


