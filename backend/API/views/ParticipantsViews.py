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

@api_view(['Get'])
def get_Participants_detail(request, key, format = None):
    participant = get_object_or_404(Participant,pk=key)
    if request.method == 'GET':
        serializer = ParticipantsSerializer(participant)
        return Response(serializer.data)
    
@api_view(['Put'])
def put_Participants_detail(request, key, format = None):
    participant = get_object_or_404(Participant, pk=key)
    serializer = ParticipantsSerializer(participant, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Put'])
def delete_Participant_detail(request, key, format = None):
    participant = get_object_or_404(Participant, pk=key)
    participant.status = 'N'
    participant.save()
    serializer = ParticipantsSerializer(participant)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

@api_view(['Put'])
def restore_Participant_detail(request, key, format = None):
    participant = get_object_or_404(Participant, pk=key)
    participant.status = 'A'
    participant.save()
    serializer = ParticipantsSerializer(participant)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)