from .models import *
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from collections import OrderedDict

class ParticipantsSerializer(ModelSerializer):
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

    class Meta:
        model = Participant
        fields = '__all__'

class UserSerializer(ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_moderator = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    is_active = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = User
        fields = '__all__'

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class RequestSerializer(ModelSerializer):
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

    class Meta:
        model = Request
        fields = '__all__'

class RequestParticipantSerializer(ModelSerializer):
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

    class Meta:
        model = RequestParticipant
        fields = '__all__'

class PositionSerializer(ModelSerializer):
    class Meta:
        model = RequestParticipant
        fields = ["is_capitan","Participant"]