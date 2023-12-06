from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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

from datetime import datetime


session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

def checkStatusUpdate(old, new, isModer):
    return ((not isModer) and (new in ['P', 'D']) and (old == 'I')) or (isModer and (new in ['A', 'W']) and (old == 'P'))

def getParticipantInRequsetWithImage(serializer: ParticipantsSerializer):
    minio = MinioClass()
    ParticipantData = serializer.data
    ParticipantData.update({'image': minio.getImage('images', serializer.data['id'], serializer.data['file_extension'])})
    return ParticipantData

# добавляет данные продукта ко всем позициям заказа
def getRequestPositionsWithParticipantData(serializer: PositionSerializer):
    positions = []
    for item in serializer.data:
        participant = get_object_or_404(Participant, pk=item['Participant'])
        positionData = item
        positionData['participant_data'] = getParticipantInRequsetWithImage(ParticipantsSerializer(participant))
        positions.append(positionData)
    return positions

class requestList_view(APIView):
    # получение списка заказов
    # можно только если авторизован
    @swagger_auto_schema(operation_description="Данный метод возвращает список всех заказов(если модератор) или только список созданных пользователем заказов(клиент). Доступ: только если авторизован.")
    def get(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        currentUser = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if currentUser.is_moderator:
            application = filterRequest(Request.objects.all(), request)
        else:
            application = filterRequest(Request.objects.filter(user_id=currentUser.pk), request)

        serializer = RequestSerializer(application, many=True)
        wideApplication = serializer.data
        for i, wa in enumerate(serializer.data):
            user = get_object_or_404(User, pk=wa['user_id'])
            moder = get_object_or_404(User, pk=wa['moder_id'])
            wideApplication[i]['user_name'] = user.username
            wideApplication[i]['moder_name'] = moder.username
        return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
    
    # отправка заказа пользователем
    # можно только если авторизован
    @swagger_auto_schema(operation_description="Данный метод реализует отправку созданного заказа пользователем. Доступ: только если авторизован.", request_body=RequestSerializer)
    def put(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        application = get_object_or_404(Request, pk=getOrderID(request))
        new_status = "P"
        if checkStatusUpdate(application.status, new_status, isModer=False):
            application.status = new_status
            application.send = datetime.now()
            application.save()
            wideApplication = RequestSerializer(application).data
            wideApplication['user_name'] = User.objects.get(pk = wideApplication['user_id']).username
            wideApplication['moder_name'] = User.objects.get(pk = wideApplication['moder_id']).username
            return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление заказа пользователем
    # можно только если авторизован
    @swagger_auto_schema(operation_description="Данный метод реализовывает удаление заказа пользователем. Доступ: только если авторизован.")
    def delete(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        new_status = "D"
        application = get_object_or_404(Request, pk=getOrderID(request))
        if checkStatusUpdate(application.status, new_status, isModer=False):
            application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    


class requestDetail_view(APIView):
    # получение заказа
    # можно получить свой заказ если авторизован
    # если авторизован и модератор, то можно получить любой заказ
    @swagger_auto_schema(operation_description="Данный метод возвращает только свой заказ, если пользователь, или любой заказ, если модератор. Доступ: только если авторизован.")
    def get(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        currentUser = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        order_keys = Request.objects.filter(user_id=currentUser.pk).values_list('pk', flat=True)
        if (pk in order_keys) or currentUser.is_moderator:
            application = get_object_or_404(Request, pk=pk)
            applicationSerializer = RequestSerializer(application)
            wideApplication = applicationSerializer.data
            
            positions = RequestParticipant.objects.filter(Request=pk)
            positionsSerializer = PositionSerializer(positions, many=True)

            wideApplication['user_name'] = User.objects.get(pk = wideApplication['user_id']).username
            wideApplication['moder_name'] = User.objects.get(pk = wideApplication['moder_id']).username
            wideApplication['positions'] = getRequestPositionsWithParticipantData(positionsSerializer)

            return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    # перевод заказа модератором на статус A или W
    # можно только если авторизован и модератор
    @swagger_auto_schema(operation_description="Данный метод реализовывает перевод модератором на статус A или W. Доступ: только если авторизован.", request_body=RequestSerializer)
    def put(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moderator:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        application = get_object_or_404(Request, pk=pk)
        try: 
            new_status = request.data['status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if checkStatusUpdate(application.status, new_status, isModer=True):
            application.status = new_status
            application.closed = datetime.now()
            application.save()
            wideApplication = RequestSerializer(application).data
            wideApplication['user_name'] = User.objects.get(pk = wideApplication['user_id']).username
            wideApplication['moder_name'] = User.objects.get(pk = wideApplication['moder_id']).username
            return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)