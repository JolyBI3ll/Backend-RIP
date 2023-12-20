from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
import requests
import redis
from backend.settings import REDIS_HOST, REDIS_PORT, PAYMENT_PASSWORD

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

class Current_View(APIView):
    @swagger_auto_schema(operation_description="Данный метод возвращает черновую заявку. Доступ: только если авторизован.")
    def get(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        username = session_storage.get(session_id)
        if username is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        currentUser = User.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        request_current = Request.objects.filter(user_id=currentUser).filter(status='I')
        if request_current.exists():
            application = request_current.first()
            requestserializer = RequestSerializer(application)

            positions = RequestParticipant.objects.filter(Request=application.pk)
            positionsSerializer = PositionSerializer(positions, many=True)

            response = requestserializer.data
            response['positions'] = getRequestPositionsWithParticipantData(positionsSerializer)

            return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
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
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
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
            url = "http://localhost:8080/result/"
            params = {"Request_id": application.pk}
            response = requests.post(url, json=params)

            application.status = new_status
            application.send = datetime.now()
            application.save()
            wideApplication = RequestSerializer(application).data
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
            return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class EventStatus_View(APIView):
    # изменение статуса оплаты заказа
    # вызывается асинхронным сервисом
    @swagger_auto_schema(request_body=RequestSerializer)
    def put(self, request, pk, format=None):
        event_status = request.data["status"]
        password = request.data["password"]
        if password != PAYMENT_PASSWORD:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            application = Request.objects.get(pk=pk)
            application.eventstatus = event_status
            application.save()
            return Response(status=status.HTTP_200_OK)
        except Request.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)