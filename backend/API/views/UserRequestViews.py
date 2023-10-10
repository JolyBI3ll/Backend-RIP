from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view

from datetime import datetime

def checkStatusUpdate(old, new, isModer):
    return ((not isModer) and (new in ['P', 'D']) and (old == 'I')) or (isModer and (new in ['A', 'W']) and (old == 'P'))

def changeStatusByYser(user, status_):
    currentUser = User.objects.get(pk=user)
    application = get_object_or_404(Request, pk=currentUser.active_order)
    new_status = status_
    if checkStatusUpdate(application.status, new_status, isModer=False):
        currentUser.active_order = -1
        currentUser.save()
        application.status = new_status
        application.send = datetime.now()
        application.save()
        serializer = RequestSerializer(application)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get'])    
def getUserRequestPositions(request, user, format=None):
    positions = RequestParticipant.objects.filter(Request=User.objects.get(pk=user).active_order)
    serializer = PositionSerializer(positions, many=True)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

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