from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from login.models import User
from login.serializers import RegisterSerializer, LoginSerializer, MypageSerializer
from login.serializers import ChangePasswordSerializer, UserInfoUpdateSerializer, UserSerializer

from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# 공통 영역
from common.common import CommonView

from django.contrib.auth.hashers import check_password


# Register는 post만 수행
class RegisterAPI(APIView):
    # Output schema 정의
    name_field = openapi.Schema(
        description='사용자 이름',
        type=openapi.TYPE_STRING
    )
    mobile_field = openapi.Schema(
        description='사용자 전화번호',
        type=openapi.TYPE_STRING
    )
    id_field = openapi.Schema(
        description='사용자 ID',
        type=openapi.TYPE_STRING
    )
    success_response = openapi.Schema(
        title='response',
        type=openapi.TYPE_OBJECT,
        properties={
            'name': name_field,
            'mobile': mobile_field,
            'username': id_field
        }
    )
    @swagger_auto_schema(tags=["회원가입"],
                         request_body=RegisterSerializer,
                         responses={
                             200: success_response,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    def post(self, request):
        # 사용자가 입력한 회원가입 정보를 request로 받아 serializer에 담기
        serializer = RegisterSerializer(data=request.data)
        # 유효성 검사(비밀번호1, 비밀번호2 동일한 지)
        if serializer.is_valid(raise_exception=True):
            serializer.save() # serializer의 save() 요청 => 기본 create() 함수 작동
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# Login도 post만 수행
class LoginAPI(APIView):
    # Output schema 정의
    token_field = openapi.Schema(
        description='로그인 사용자의 Token',
        type=openapi.TYPE_STRING
    )
    success_response = openapi.Schema(
        title='response',
        type=openapi.TYPE_OBJECT,
        properties={
            'token': token_field
        }
    )
    @swagger_auto_schema(tags=["로그인"],
                         request_body=LoginSerializer,
                         responses={
                             200: success_response,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # raise_exceiption을 통해 raise된 에러를 전달
        token = serializer.validated_data # validated_data: validate()의 리턴값을 의미, 현재는 Token
        return Response({"token": token, "user_id": request.data['username']}, status=status.HTTP_200_OK)


# 회원 비밀번호 수정
class ChangePasswordAPI(CommonView):
    @swagger_auto_schema(tags=["비밀번호 변경"],
                         request_body=ChangePasswordSerializer,
                         responses={
                             200: '비밀번호 변경 성공',
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        # 유효성 검사
        if serializer.is_valid():
            user = get_object_or_404(User, pk=self.user_id)
            print(self.user_id)

            # check_password: DB에 저장된 사용자의 비밀번호 AND 사용자가 입력한 비밀번호 비교
            if check_password(request.data['old_password'], user.password):
                if request.data['new_password1'] == request.data['new_password2']:
                    user.set_password(request.data['new_password1'])
                    user.save()
                    return Response({"message": "success"}, status=status.HTTP_200_OK)
                raise Exception("New_Password fields didn't match.")
            raise Exception("Old_Password fields didn't match.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 권한 필요
class ManageUserAPI(CommonView):
    # 마이페이지: 사용자 이름, 전화번호, 사용자가 작성한 글 목록, 사용자가 작성한 댓글 목록
    def get(self, request):
        user = get_object_or_404(User, pk=self.user_id)
        print(user.contents.all())
        print(user.comments.all())
        serializer = MypageSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

    @swagger_auto_schema(tags=["회원정보 수정"],
                         request_body=UserInfoUpdateSerializer,
                         responses={
                             200: UserInfoUpdateSerializer,
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    # 회원 정보 수정: 이름, 전화번호, 아이디
    def put(self, request):
        user = get_object_or_404(User, pk=self.user_id)
        # 기존 User 정보를 가져오고, 사용자가 새롭게 요청한 데이터를 넣어 저장한다.
        serializer = UserInfoUpdateSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(tags=["회원탈퇴"],
                         responses={
                             204: '회원탈퇴 성공',
                             400: '입력값 유효성 검증 실패',
                             403: '인증 에러',
                             500: '서버 에러'
                         })
    # 회원 탈퇴
    def delete(self, request):
        user = get_object_or_404(User, pk=self.user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
