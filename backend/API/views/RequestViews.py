from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view

@api_view(['Get'])
def get_RequestList(request, format=None):
    application = Request.objects.all()
    serializer = RequestSerializer(application, many=True)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

@api_view(['Get'])
def get_Request_detail(request, key, format=None):
    application = get_object_or_404(Request, pk=key)
    serializer = RequestSerializer(Request)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

@api_view(['Put'])
def put_Request(request, key, format=None):
    application = get_object_or_404(Request, pk=key)
    serializer = RequestSerializer(application, data=request.data)
    if serializer.is_valid() and ((not request.data.get('status')) or application.status == request.data['status']):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)