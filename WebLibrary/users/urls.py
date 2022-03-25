from django.urls import path
from .views import UserSignUp, LoginView


urlpatterns=[
  path('signup/', UserSignUp.as_view(), name='signup'),
  path('login/', LoginView.as_view(), name='login')
]