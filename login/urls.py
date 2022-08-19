from knox.views import LogoutView
from django.urls import path
from . import views


urlpatterns = [
    path("register/", views.RegisterAPI.as_view(), name='register'),
    path("login/", views.LoginAPI.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("change_password/", views.ChangePasswordAPI.as_view(), name='change_password'),
    path("mypage/", views.ManageUserAPI.as_view(), name='manage_user'),
]