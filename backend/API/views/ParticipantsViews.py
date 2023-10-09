from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view

@api_view(['Get'])
def get_Participants(request, format=None):
    Participants = Participant.objects.all().order_by('last_modified')
    serializer = ParticipantsSerializer(Participants, many = True)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

@api_view(['Post'])
def post_Participants(request, format=None):
    serializer = ParticipantsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
