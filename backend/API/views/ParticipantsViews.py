from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import permission_classes
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

import redis
from backend.settings import REDIS_HOST, REDIS_PORT

from ..models import *
from ..serializers import *
from ..filters import *
from ..permissions import *
from ..services import *
from api.minio.MinioClass import MinioClass

import random


session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

def getParticipantDataWithImage(serializer: ParticipantsSerializer):
    minio = MinioClass()
    ParticipantData = serializer.data
    ParticipantData.update({'image': minio.getImage('images', serializer.data['id'], serializer.data['file_extension'])})
    return ParticipantData

def postParticipantImage(request, serializer: ParticipantsSerializer):
    minio = MinioClass()
    image_file = request.FILES.get('image')
    byte_image = image_file.read()
    minio.addImage('images', serializer.data['id'], byte_image, serializer.data['file_extension'])

def putParticipantImage(request, serializer: ParticipantsSerializer):
    minio = MinioClass()
    minio.removeImage('images', serializer.data['id'], serializer.data['file_extension'])
    image_file = request.FILES.get('image')
    byte_image = image_file.read()
    minio.addImage('images', serializer.data['id'], byte_image, serializer.data['file_extension'])


class Participantlist_view(APIView):
    def get(self, request, format=None):
        requestid = getOrderID(request)
        List = {
            'RequestId': requestid
        }
        Participants = filterParticipant(Participant.objects.filter(status = 'A').order_by('pk'), request)
        ParticipantsData = [getParticipantDataWithImage(ParticipantsSerializer(participant)) for participant in Participants]
        List ['Participants'] = ParticipantsData
        return Response(List, status=status.HTTP_202_ACCEPTED)
    
    @method_permission_classes((IsModerator,))
    @swagger_auto_schema(request_body=ParticipantsSerializer)
    def post(self, request, format=None):
        serializer = ParticipantsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postParticipantImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParticipantDetail_view(APIView):
    def get(self, request, pk, format=None):
        participant = get_object_or_404(Participant,pk=pk)
        serializer = ParticipantsSerializer(participant)
        return Response(getParticipantDataWithImage(serializer), status=status.HTTP_202_ACCEPTED)
    
    def post(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        userId = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))

        RequestId = getOrderID(request)
        if RequestId == -1:   
            Request_new = {}      
            Request_new['user_id'] = userId.pk
            Request_new['moder_id'] = random.choice(User.objects.filter(is_moderator=True)).pk
            requestserializer = RequestSerializer(data=Request_new)
            if requestserializer.is_valid():
                requestserializer.save()  
                RequestId = requestserializer.data['id']
            else:
                return Response(RequestSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        if Request.objects.get(pk=RequestId).status != 'I' or len(RequestParticipant.objects.filter(Participant=pk).filter(Request=RequestId)) != 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        link = {}
        link['Participant'] = pk
        link['Request'] = RequestId
        link['is_capitan'] = False
        serializer = RequestParticipantSerializer(data=link)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=ParticipantsSerializer)
    def put(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moderator:
            return Response(status=status.HTTP_403_FORBIDDEN)

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

    def delete(self, request, pk, format = None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moderator:
            return Response(status=status.HTTP_403_FORBIDDEN)

        participant = get_object_or_404(Participant, pk=pk)
        participant.status = 'N' if participant.status == 'A' else 'A'
        participant.save()
        serializer = ParticipantsSerializer(participant)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
