from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from datetime import datetime
from .getUserId import *
from ..minio.MinioClass import MinioClass
from ..filters import *

def checkStatusUpdate(old, new, isModer):
    return ((not isModer) and (new in ['P', 'D']) and (old == 'I')) or (isModer and (new in ['A', 'W']) and (old == 'P'))

def getParticipantInRequsetWithImage(serializer: ParticipantsSerializer):
    minio = MinioClass()
    ParticipantData = serializer.data
    ParticipantData['image'] = minio.getImage('images', serializer.data['id'], serializer.data['file_extension'])
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

@api_view(['Get', 'Put', 'Delete'])
def process_Request_List(request, format=None):

    # получение списка заказов
    if request.method == 'GET':
        application = filterRequest(Request.objects.all(), request)
        serializer = RequestSerializer(application, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    # отправка заказа пользователем
    elif request.method == 'PUT':
        userId = getUserId()
        currentUser = User.objects.get(pk=userId)
        application = get_object_or_404(Request, pk=currentUser.active_request)
        new_status = "P"
        if checkStatusUpdate(application.status, new_status, isModer=False):
            currentUser.active_request = -1
            currentUser.save()
            application.status = new_status
            application.send = datetime.now()
            application.save()
            serializer = RequestSerializer(application)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление заказа пользователем
    elif request.method == 'DELETE':
        userId = getUserId()
        currentUser = User.objects.get(pk=userId)
        new_status = "D"
        application = get_object_or_404(Request, pk=currentUser.active_request)
        if checkStatusUpdate(application.status, new_status, isModer=False):
            currentUser.active_request = -1
            currentUser.save()
            application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# @api_view(['Get','Put'])
# def process_Request_detail(request, pk, format=None):

#     if request.method == 'GET':
#         userId = getUserId()
#         application = get_object_or_404(Request, pk=pk)
#         applicationserializer = RequestSerializer(application)
#         positions = RequestParticipant.objects.filter(Request=User.objects.get(pk=userId).active_request)
#         positionsSerializer = PositionSerializer(positions, many=True)
#         response = applicationserializer.data
#         response['positions'] = positionsSerializer.data
#         return Response(response, status=status.HTTP_202_ACCEPTED)
    
#     elif request.method == 'POST':
#         application = get_object_or_404(Request, pk=pk)
#         serializer = RequestSerializer(application, data=request.data)
#         if serializer.is_valid() and ((not request.data.get('status')) or application.status == request.data['status']):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get', 'Put', 'Delete'])
def process_Request_detail(request, pk, format=None):

    # получение заказа
    if request.method == 'GET':
        application = get_object_or_404(Request, pk=pk)
        applicationSerializer = RequestSerializer(application)

        positions = RequestParticipant.objects.filter(Request=pk)
        positionsSerializer = PositionSerializer(positions, many=True)

        response = applicationSerializer.data
        response['positions'] = getRequestPositionsWithParticipantData(positionsSerializer)

        return Response(response, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'PUT':
        application = get_object_or_404(Request, pk=pk)
        serializer = RequestSerializer(application, data=request.data)
        if 'status' in request.data.keys():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # перевод заказа модератором на статус A или W
    elif request.method == 'DELETE':
        application = get_object_or_404(Request, pk=pk)
        try: 
            new_status = request.data['status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if checkStatusUpdate(application.status, new_status, isModer=True):
            application.status = new_status
            application.closed = datetime.now()
            application.save()
            serializer = RequestSerializer(application)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
