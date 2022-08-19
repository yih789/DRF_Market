from rest_framework.views import APIView

class CommonView(APIView):
    # 내가 정의한 변수
    user_id = ''
    version = ''

    # APIView에 dispatch 함수를 오버라이딩
    # 자식의 함수가 먼저 호출된 다음 부모 함수를 호출하도록 한다.
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.headers.get('id', False)
        self.version = request.headers.get('version', False)

        return super(CommonView, self).dispatch(request, *args, **kwargs)