from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .getUserId import *
import random
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from ..minio.MinioClass import MinioClass
from ..filters import *
   
def getInputtingId():
    requestlist = Request.objects.filter(user_id = getUserId()).filter(status = 'I')
    if not requestlist.exists():
        return -1
    else:
        return requestlist[0].pk

def getParticipantDataWithImage(serializer: ParticipantsSerializer):
    minio = MinioClass()
    ParticipantData = serializer.data
    ParticipantData.update({'image': minio.getImage('images', serializer.data['id'], serializer.data['file_extension'])})
    return ParticipantData

def postParticipantImage(request, serializer: ParticipantsSerializer):
    minio = MinioClass()
    minio.addImage('images', serializer.data['id'], request.data['image'], serializer.data['file_extension'])

# изменяет картинку продукта в minio на переданную в request
def putParticipantImage(request, serializer: ParticipantsSerializer):
    minio = MinioClass()
    minio.removeImage('images', serializer.data['id'], serializer.data['file_extension'])
    minio.addImage('images', serializer.data['id'], request.data['image'], serializer.data['file_extension'])

@api_view(['Get', 'Post'])
def process_Participant_list(request, format=None):
    if request.method == 'GET':
        requestid = getInputtingId()
        List = {
            'RequestId': requestid
        }
        Participants = filterParticipant(Participant.objects.filter(status = 'A').order_by('pk'), request)
        ParticipantsData = [getParticipantDataWithImage(ParticipantsSerializer(participant)) for participant in Participants]
        List ['Participants'] = ParticipantsData
        return Response(List, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST':
        serializer = ParticipantsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postParticipantImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Get', 'Post', 'Put', 'Delete'])
def procces_Participant_detail(request, pk, format=None):
    if request.method == 'GET':
        participant = get_object_or_404(Participant,pk=pk)
        serializer = ParticipantsSerializer(participant)
        return Response(getParticipantDataWithImage(serializer), status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST':
        userId = getUserId()
        RequestId = getInputtingId()
        if RequestId == -1:   
            Request_new = {}      
            Request_new['user_id'] = userId
            Request_new['moder_id'] = random.choice(User.objects.filter(is_moderator=True)).pk
            requestserializer = RequestSerializer(data=Request_new)
            if requestserializer.is_valid():
                requestserializer.save()  
                RequestId = requestserializer.data['id']
            else:
                return Response(RequestSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        # if Request.objects.get(pk=RequestId).status != 'I' or len(RequestParticipant.objects.filter(pk=pk).filter(Request=RequestId)) != 0:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        link = {}
        link['Participant'] = pk
        link['Request'] = RequestId
        link['is_capitan'] = False
        serializer = RequestParticipantSerializer(data=link)
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
        if 'id' in fields or 'status' in fields or 'last_modified' in fields:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = ParticipantsSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if 'image' in fields:
                putParticipantImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)