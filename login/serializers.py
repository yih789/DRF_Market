from rest_framework import serializers
from .models import User

from django.contrib.auth.password_validation import validate_password
from knox.models import AuthToken

from django.contrib.auth import authenticate

from content.serializers import CommentCreateSerializer, ContentCreateSerializer

# read_only: API 출력에는 포함되지만 입력에는 포함되지 않는 필드
# write_only: 인스턴스 생성 시에는 입력에 포함되지만 직렬화에는 포함되지 않게
# required: 역직렬화 중에 제공되지 않으면 오류 발생
class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        help_text="비밀번호"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        help_text="비밀번호 확인"
    )

    class Meta:
        model = User
        fields = ["name", "mobile", "username", "password1", "password2"]

    # 유효성 검사
    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    # save() 발생 시
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            mobile=validated_data['mobile'],
            name=validated_data['name'],
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user


# User 모델과 무관하다. 왜냐면 Token 방식으로 인증
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, help_text="비밀번호")

    # 사용자가 입력한 ID, PW를 통해 토큰 검사 수행
    def validate(self, data):
        user = authenticate(**data)
        # 가입한 사용자가 맞다면 토큰 반환
        if user:
            token = AuthToken.objects.create(user=user)[1]
            return token
        # 사용자 인증 실패하면 에러 출력
        raise serializers.ValidationError({"error": "로그인 실패"})


# 비밀번호 수정
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True, help_text="기존 비밀번호")
    new_password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password], help_text="새 비밀번호")
    new_password2 = serializers.CharField(write_only=True, required=True, help_text="새 비밀번호 확인")


# 회원정보 수정
class UserInfoUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    mobile = serializers.CharField(required=False)
    username = serializers.CharField(required=False)


class MypageSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    mobile = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    comments = CommentCreateSerializer(many=True, read_only=True)
    contents = ContentCreateSerializer(many=True, read_only=True)



class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["name", "mobile", "username"]

