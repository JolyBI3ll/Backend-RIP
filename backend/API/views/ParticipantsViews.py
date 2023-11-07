from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .getUserId import *
from random import random
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from ..minio.MinioClass import MinioClass

def getProductDataWithImage(serializer: ParticipantsSerializer):
    minio = MinioClass()
    ParticipantData = serializer.data
    ParticipantData['image'] = minio.getImage('images', serializer.data['id'], serializer.data['file_extension'])
    return ParticipantData

def postProductImage(request, serializer: ParticipantsSerializer):
    minio = MinioClass()
    minio.addImage('images', serializer.data['id'], request.data['image'], serializer.data['file_extension'])

def putProductImage(request, serializer: ParticipantsSerializer):
    minio = MinioClass()
    minio.removeImage('images', serializer.data['id'], serializer.data['file_extension'])
    minio.addImage('images', serializer.data['id'], request.data['image'], serializer.data['file_extension'])

@api_view(['Get', 'Post'])
def process_Participant_list(request, format=None):
    if request.method == 'GET':
        Participants = Participant.objects.all().order_by('id')
        ParticipantsData = [getProductDataWithImage(ParticipantsSerializer(participant)) for participant in Participants]
        return Response(ParticipantsData, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST':
        serializer = ParticipantsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postProductImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Get', 'Post', 'Put', 'Delete'])
def procces_Participant_detail(request, pk, format=None):
    if request.method == 'GET':
        participant = get_object_or_404(Participant,pk=pk)
        serializer = ParticipantsSerializer(participant)
        return Response(getProductDataWithImage(serializer), status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST':
        userId = getUserId()
        currentUser = User.objects.get(pk=userId)
        RequestId = currentUser.active_request
        if RequestId == -1:   
            Request_new = {}      
            Request_new['user_id'] = userId
            Request_new['moder_id'] = random.choice(User.objects.filter(is_moderator=True)).pk
            requestserializer = RequestSerializer(data=Request)
            if requestserializer.is_valid():
                requestserializer.save()  
                RequestId = requestserializer.data['pk']
                currentUser.active_request = RequestId
                currentUser.save()
            else:
                return Response(RequestSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        if Request.objects.get(pk=RequestId).status != 'I' or len(RequestParticipant.objects.filter(pk=pk).filter(Request=RequestId)) != 0:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        link = {}
        link['Participant'] = pk
        link['Request'] = RequestId
        serializer = RequestParticipant(data=link)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try: 
            new_status = request.data['status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        participant = get_object_or_404(Participant, pk=pk)
        participant.status = new_status
        participant.save()
        serializer = ParticipantsSerializer(participant)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'PUT':
        product = get_object_or_404(Participant, pk=pk)
        fields = request.data.keys()
        if 'pk' in fields or 'status' in fields or 'last_modified' in fields:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = ParticipantsSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if 'image' in fields:
                putProductImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)