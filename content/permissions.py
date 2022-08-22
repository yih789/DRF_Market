from rest_framework import permissions

class ContentPermission(permissions.BasePermission):
    #글 조회: 누구나, 생성: 로그인 유저, 편집: 글 작성자
    def has_permission(self, request, view): #객체 전체 권한
        # list Read: 누구나
        if request.method == 'GET':
            return True
        # obj create: 로그인 유저
        return request.user.is_authenticated


class CommentPermission(permissions.BasePermission):
    #글 조회: 누구나, 생성: 로그인 유저, 편집: 글 작성자
    def has_permission(self, request, view): #객체 전체 권한
        # list Read: 누구나
        if request.method == 'GET':
            return True
        # obj create: 로그인 유저
        print(request.user)
        return request.user.is_authenticated