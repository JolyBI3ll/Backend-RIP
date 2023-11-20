from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from .getUserId import getUserId

def getInputtingId():
    requestlist = Request.objects.filter(user_id = getUserId()).filter(status = 'I')
    if not requestlist.exists():
        return -1
    else:
        return requestlist[0].pk

@api_view(['Delete', 'Put'])
def process_MM(request, format = None):
    if request.method == 'PUT':
        try: 
            is_capitan = request.data['is_capitan']
            participantId = request.data['participant']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        links = RequestParticipant.objects.filter(Participant=participantId).filter(Request=getInputtingId())
        if len(links) > 0:
            links[0].is_capitan = is_capitan
            links[0].save()
            return Response(PositionSerializer(links[0]).data, status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление продукта из заказа
    elif request.method == 'DELETE':
        try: 
            participantId = request.data['participant']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        links = RequestParticipant.objects.filter(Participant=participantId).filter(Request=getInputtingId())
        if len(links) > 0:
            links[0].delete()
            if len(RequestParticipant.objects.filter(Request=getInputtingId())) == 0:
                Request.objects.get(pk=getInputtingId()).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)