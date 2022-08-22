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

from rest_framework.exceptions import ParseError

# 로거 사용
import logging
logger = logging.getLogger('error')


# Content CREATE
class ContentCreateAPI(CommonView):
    permission_classes = [ContentPermission]

    @swagger_auto_schema(tags=["게시글 생성"],
                         request_body=ContentCreateSerializer,
                         responses={
                             200: ContentCreateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         },
                         manual_parameters=[
                             openapi.Parameter('Authorization', openapi.IN_HEADER, description="AUTH",
                                               type=openapi.TYPE_STRING)]
                         )
    def post(self, request):  # CREATE
        user = get_object_or_404(User, pk=request.user)
        serializer = ContentCreateSerializer(data=request.data)  # request
        if serializer.is_valid():
            serializer.save(writer_id=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # response
        logger.error('회원가입 정보 입력 실패')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Content READ_LIST => list, filter_list
# Pagination
class ContentListAPI(APIView, PaginationHandlerMixin):
    pagination_class = ContentsPagination
    serializer_class = ContentSerializer

    @swagger_auto_schema(tags=["게시글 목록"],
                         request_body=None,
                         responses={
                             200: ContentCreateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    # READ list
    def get(self, request, format=None, *args, **kwargs):
        instance = Content.objects.all()
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(instance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    word_field = openapi.Schema(
        description='검색 키워드',
        type=openapi.TYPE_STRING,
    )
    word_request = openapi.Schema(
        title='request',
        type=openapi.TYPE_OBJECT,
        properties={
            'word': word_field
        }
    )
    @swagger_auto_schema(tags=["게시글 필터 목록"],
                         request_body=word_request,
                         responses={
                             200: ContentCreateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    # READ filter_list
    def post(self, request, format=None, *args, **kwargs):
        word = request.data['word']

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

    def get_object(self, content_id):
        content = get_object_or_404(Content, pk=content_id)
        self.check_object_permissions(self.request, content)
        return content

    @swagger_auto_schema(tags=["하나의 게시글 조회"],
                         request_body=None,
                         responses={
                             200: ContentCreateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    # READ RETRIEVE
    def get(self, request, content_id):
        content = self.get_object(content_id)
        serializer = ContentSerializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["하나의 게시글 수정"],
                         request_body=ContentCreateSerializer,
                         responses={
                             200: ContentCreateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         },
                         manual_parameters=[
                             openapi.Parameter('Authorization', openapi.IN_HEADER, description="AUTH",
                                               type=openapi.TYPE_STRING)]
                         )
    # UPDATE
    def put(self, request, content_id):
        content = self.get_object(content_id)
        serializer = ContentCreateSerializer(content, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error('게시글 수정 입력 실패')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=["하나의 게시글 삭제"],
                         request_body=None,
                         responses={
                             200: 'success delete',
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         },
                         manual_parameters=[
                             openapi.Parameter('Authorization', openapi.IN_HEADER, description="AUTH",
                                               type=openapi.TYPE_STRING)]
                         )
    # DELETE
    def delete(self, request, content_id):
        content = self.get_object(content_id)
        content.delete()  # 삭제
        return Response({"massage": "success delete"}, status=status.HTTP_200_OK)


# Comment: pk 필요 x
class CommentsAPI(CommonView):
    permission_classes = [CommentPermission]

    @swagger_auto_schema(tags=["댓글 생성"],
                         request_body=CommentCreateSerializer,
                         responses={
                             200: CommentCreateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         },
                         manual_parameters=[
                             openapi.Parameter('Authorization', openapi.IN_HEADER, description="AUTH",
                                               type=openapi.TYPE_STRING)]
                         )
    # CREATE
    def post(self, request):  # CREATE
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, pk=request.user)
            serializer.save(commenter_id=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error('댓글 입력 실패')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Comment: pk 필요
class CommentAPI(APIView):
    permission_classes = [CommentPermission]

    def get_object(self, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        self.check_object_permissions(self.request, comment)
        return comment

    text_field = openapi.Schema(
        description='검색 키워드',
        type=openapi.TYPE_STRING,
    )
    text_request = openapi.Schema(
        title='request',
        type=openapi.TYPE_OBJECT,
        properties={
            'text': text_field
        }
    )
    @swagger_auto_schema(tags=["댓글 수정"],
                         request_body=text_request,
                         responses={
                             200: CommentCreateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         },
                         manual_parameters=[
                             openapi.Parameter('Authorization', openapi.IN_HEADER, description="AUTH",
                                               type=openapi.TYPE_STRING)]
                         )
    # UPDATE
    def put(self, request, comment_id):
        comment = self.get_object(comment_id)
        if request.data.get('text') == '': # 댓글로 빈 문자열을 넣으면
            raise ParseError("댓글을 작성하세요.")

        comment.text = request.data.get('text', comment.text)
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=["댓글 삭제"],
                         request_body=None,
                         responses={
                             200: 'success delete',
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         },
                         manual_parameters=[
                             openapi.Parameter('Authorization', openapi.IN_HEADER, description="AUTH",
                                               type=openapi.TYPE_STRING)]
                         )
    # DELETE
    def delete(self, request, comment_id):
        comment = self.get_object(comment_id)
        comment.delete()  # 삭제
        return Response({"massage": "success delete"}, status=status.HTTP_200_OK)


