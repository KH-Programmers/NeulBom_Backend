from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
import requests
from rest_framework import generics
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import CustomUser as User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, JSONParser
from django.contrib.auth import authenticate



def captchaVerify(token: str):
    """
    Cloudflare Verify function.
    :param token: cf-turnstile-response

    :return: boolean
    """
    
    
    resp = requests.post(
        "https://hcaptcha.com/siteverify",
        data={
            "secret": "0x34B068bDAF1FFAad08543bbA756B2bF711190416",
            "response": token,
        }
    ).json()
    return resp["success"]


class LoginView(KnoxLoginView):
    """
    로그인
    """

    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return super(LoginView, self).post(request, format=None)
        else:
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    회원가입
    """

    queryset = User.objects.all()
    permission_classes = [AllowAny,]
    parser_classes = [JSONParser, MultiPartParser]

    def post(self, request):
        if User.objects.filter(username=request.data["username"]).exists():
            return Response(status=status.HTTP_409_CONFLICT)

        serializer = RegisterSerializer(data=request.data)

        if not captchaVerify(request.data["token"]):
            return Response(
                {"error": "Invalid turnstile token"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)


class Profile(APIView):
    def get(self, request, pk):
        profile = get_object_or_404(User, id=pk)
        serializer = UserSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk):
        profile = get_object_or_404(User, id=pk)
        serializer = UserSerializer(profile, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = get_object_or_404(User, id=pk)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#class token_validation(APIView):
#   def get(self, request, pk):
#

class Authentication(APIView):
    def get(self, request):
        user = request.auth
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_200_OK)
