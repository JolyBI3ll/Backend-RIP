from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from datetime import datetime
from .getUserId import *

def checkStatusUpdate(old, new, isModer):
    return ((not isModer) and (new in ['P', 'D']) and (old == 'I')) or (isModer and (new in ['A', 'W']) and (old == 'P'))

def changeStatusByYser(user, status_):
    currentUser = User.objects.get(pk=user)
    application = get_object_or_404(Request, pk=currentUser.active_request)
    new_status = status_
    if checkStatusUpdate(application.status, new_status, isModer=False):
        currentUser.active_request = -1
        currentUser.save()
        application.status = new_status
        application.send = datetime.now()
        application.save()
        serializer = RequestSerializer(application)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['Get'])
def process_RequestList(request, format=None):

    application = Request.objects.all()
    serializer = RequestSerializer(application, many=True)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

@api_view(['Get','Put'])
def process_Request_detail(request, pk, format=None):

    if request.method == 'GET':
        userId = getUserId()
        application = get_object_or_404(Request, pk=pk)
        applicationserializer = RequestSerializer(application)
        positions = RequestParticipant.objects.filter(Request=User.objects.get(pk=userId).active_request)
        positionsSerializer = PositionSerializer(positions, many=True)
        response = applicationserializer.data
        response['positions'] = positionsSerializer.data
        return Response(response, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST':
        application = get_object_or_404(Request, pk=pk)
        serializer = RequestSerializer(application, data=request.data)
        if serializer.is_valid() and ((not request.data.get('status')) or application.status == request.data['status']):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

##----------------------------------------------------------------------------------------------------------------------

@api_view(['Put'])
def sendRequest(request, user, format=None):
    return changeStatusByYser(user, "P")

@api_view(['Put'])
def deleteRequest(request, user, format=None):    
    return changeStatusByYser(user, "D")

@api_view(['Put'])
def closeRequest(request, key, format=None):
    application = get_object_or_404(Request, pk=key)
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