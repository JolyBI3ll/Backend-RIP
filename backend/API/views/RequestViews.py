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

def getInputtingId():
    requestlist = Request.objects.filter(user_id = getUserId()).filter(status = 'I')
    if not requestlist.exists():
        return -1
    else:
        return requestlist[0].pk

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
        wideApplication = serializer.data
        for i, wa in enumerate(serializer.data):
            user = get_object_or_404(User, pk=wa['user_id'])
            moder = get_object_or_404(User, pk=wa['moder_id'])
            wideApplication[i]['user_name'] = user.name
            wideApplication[i]['moder_name'] = moder.name
        return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
    
    # отправка заказа пользователем
    elif request.method == 'PUT':
        application = get_object_or_404(Request, pk=getInputtingId())
        new_status = "P"
        if checkStatusUpdate(application.status, new_status, isModer=False):
            application.status = new_status
            application.send = datetime.now()
            application.save()
            wideApplication = RequestSerializer(application).data
            wideApplication['user_name'] = User.objects.get(pk = wideApplication['user_id']).name
            wideApplication['moder_name'] = User.objects.get(pk = wideApplication['moder_id']).name
            return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление заказа пользователем
    elif request.method == 'DELETE':
        new_status = "D"
        application = get_object_or_404(Request, pk=getInputtingId())
        if checkStatusUpdate(application.status, new_status, isModer=False):
            application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['Get', 'Put'])
def process_Request_detail(request, pk, format=None):

    # получение заказа
    if request.method == 'GET':
        application = get_object_or_404(Request, pk=pk)
        applicationSerializer = RequestSerializer(application)
        wideApplication = applicationSerializer.data
        
        positions = RequestParticipant.objects.filter(Request=pk)
        positionsSerializer = PositionSerializer(positions, many=True)

        wideApplication['user_name'] = User.objects.get(pk = wideApplication['user_id']).name
        wideApplication['moder_name'] = User.objects.get(pk = wideApplication['moder_id']).name
        wideApplication['positions'] = getRequestPositionsWithParticipantData(positionsSerializer)

        return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'PUT':
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
            wideApplication['user_name'] = User.objects.get(pk = wideApplication['user_id']).name
            wideApplication['moder_name'] = User.objects.get(pk = wideApplication['moder_id']).name
            return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)