from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_yasg.utils import swagger_auto_schema

import redis
from backend.settings import REDIS_HOST, REDIS_PORT

from ..models import *
from ..serializers import *
from ..services import *


session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


class links_view(APIView):
    # Изменение статуса "Капитан?"
    # можно только если авторизован
    @swagger_auto_schema(request_body=RequestParticipantSerializer)
    def put(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try: 
            is_capitan = request.data['is_capitan']
            participantId = request.data['participant']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        links = RequestParticipant.objects.filter(Participant=participantId).filter(Request=getOrderID(request))
        if len(links) > 0:
            links[0].is_capitan = is_capitan
            links[0].save()
            return Response(PositionSerializer(links[0]).data, status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление продукта из заказа
    # можно только если авторизован
    @swagger_auto_schema(request_body=RequestParticipantSerializer)
    def delete(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try: 
            participantId = request.data['participant']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        links = RequestParticipant.objects.filter(Participant=participantId).filter(Request=getOrderID(request))
        if len(links) > 0:
            links[0].delete()
            if len(RequestParticipant.objects.filter(Request=getOrderID(request))) == 0:
                Request.objects.get(pk=getOrderID(request)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)