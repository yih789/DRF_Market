from rest_framework import serializers
from .models import User

from django.contrib.auth.password_validation import validate_password
from knox.models import AuthToken

from django.contrib.auth import authenticate

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

'''
    def validate(self, data):
        user = get_object_or_404(User, pk=self.user_id)
        # check_password: DB에 저장된 사용자의 비밀번호 AND 사용자가 입력한 비밀번호 비교
        if check_password(data['old_password'], user.password):
            if data['new_password1'] == data['new_password2']:
                return True
            raise serializers.ValidationError({"password": "New_Password fields didn't match."})
        raise serializers.ValidationError({"password": "Old_Password fields didn't match."})

    def create(self, validated_data):
        self.user.set_password(validated_data['new_password1'])
        self.user.save()
        return self.user
'''


# 회원정보 수정
class UserInfoUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    mobile = serializers.CharField(required=False)
    username = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        # 기존 객체의 정보를 사용자가 입력한 정보로 바꾸거나, 입력하지 않았다면 기존 내용 그대로 유지
        instance.name = validated_data.get('name', instance.name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.username = validated_data.get('username', instance.username)
        return instance


class MypageSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = []
        # 이름, 전화번호, 아이디, 사용자가 작성한 게시글, 사용자가 작성한 댓글


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ["name", "mobile", "username"]

