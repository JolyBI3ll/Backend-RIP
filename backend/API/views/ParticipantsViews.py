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

from api.views.RequestViews import getRequestPositionsWithParticipantData

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
minio = MinioClass()

def getParticipantDataWithImage(serializer: RequestSerializer):
    ParticipantData = serializer.data
    ParticipantData.update({'image': minio.getImage('images', serializer.data['id'], serializer.data['file_extension'])})
    return ParticipantData

def postParticipantImage(request, serializer: RequestSerializer):
    minio.addImage('images', serializer.data['id'], request.data['image'], serializer.data['file_extension'])

# изменяет картинку продукта в minio на переданную в request
def putParticipantImage(request, serializer: RequestSerializer):
    minio.removeImage('images', serializer.data['id'], serializer.data['file_extension'])
    minio.addImage('images', serializer.data['id'], request.data['image'], serializer.data['file_extension'])

# def postParticipantImage(request, serializer: ParticipantsSerializer):
#     minio = MinioClass()
#     image_file = request.FILES.get('image')
#     byte_image = image_file.read()
#     minio.addImage('images', serializer.data['id'], byte_image, serializer.data['file_extension'])

# def putParticipantImage(request, serializer: ParticipantsSerializer):
#     minio = MinioClass()
#     minio.removeImage('images', serializer.data['id'], serializer.data['file_extension'])
#     image_file = request.FILES.get('image')
#     byte_image = image_file.read()
#     minio.addImage('images', serializer.data['id'], byte_image, serializer.data['file_extension'])


class Participantlist_view(APIView):
    @swagger_auto_schema(operation_description="Данный метод возвращает инденитификатор черновика и список всех участников, зарегестрированных на нашем сайте. Доступ: все")
    def get(self, request, format=None):
        requestid = getOrderID(request)
        List = {
            'RequestId': requestid
        }
        Participants = filterParticipant(Participant.objects.order_by('pk'), request)
        ParticipantsData = [getParticipantDataWithImage(ParticipantsSerializer(participant)) for participant in Participants]
        List ['Participants'] = ParticipantsData
        return Response(List, status=status.HTTP_202_ACCEPTED)
    
    @swagger_auto_schema(operation_description="Данный метод добавляет нового участника. Доступ: все.", request_body=ParticipantsSerializer)
    def post(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moderator:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ParticipantsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postParticipantImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParticipantDetail_view(APIView):
    @swagger_auto_schema(operation_description="Данный метод возвращает данные о конкретном участнике по идентификатору. Доступ: все.")
    def get(self, request, pk, format=None):
        participant = get_object_or_404(Participant,pk=pk)
        serializer = ParticipantsSerializer(participant)
        return Response(getParticipantDataWithImage(serializer), status=status.HTTP_202_ACCEPTED)
    
    @swagger_auto_schema(operation_description="Данный метод добавляет услугу в заявку. Если заявки не существует, то создает ее. Доступ: только если авторизован.")
    def post(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        userId = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        RequestId = getOrderID(request)
        if RequestId == -1:   # если его нету
            request_new = Request.objects.create(
                user_id=userId,
                moder_id=random.choice(User.objects.filter(is_moderator=True))
            )
            RequestId = request_new.pk
            
        # теперь у нас точно есть черновик, поэтому мы создаём связь м-м (не уверен что следующие две строки вообще нужны)    
        if Request.objects.get(pk=RequestId).status != 'I' or len(RequestParticipant.objects.filter(Participant=pk).filter(Request=RequestId)) != 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        RequestParticipant.objects.create(
            Participant_id=pk,
            Request_id=RequestId,
            is_capitan = False
        )
        
        request_new = Request.objects.get(pk=RequestId)
        requestserializer = RequestSerializer(request_new)

        positions = RequestParticipant.objects.filter(Request=request_new.pk)
        positionsSerializer = PositionSerializer(positions, many=True)

        response = requestserializer.data
        response['positions'] = getRequestPositionsWithParticipantData(positionsSerializer)
        return Response(response, status=status.HTTP_202_ACCEPTED)
    


    @swagger_auto_schema(operation_description="Данный метод изменяет поля участника. Доступ: только если авторизован и модератор.", request_body=ParticipantsSerializer)
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

    @swagger_auto_schema(operation_description="Данный метод выполняет логическое удаление/восстановление участника. Доступ: только если авторизован и модератор.")
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
