from django.contrib.auth import authenticate, logout, login
from rest_framework.decorators import authentication_classes
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema

from datetime import timedelta

import uuid

from ..serializers import *
from rest_framework.decorators import api_view
# from glasses_api.permissions import *
# from ..services import get_session

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
def login_view(request):
    email = request.POST["email"] # допустим передали username и password
    password = request.POST["password"]
    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse("{'status': 'ok'}")
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")

def logout_view(request):
    logout(request._request)
    return Response({'status': 'Success'})