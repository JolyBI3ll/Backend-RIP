from django.contrib import admin
from .models import *

admin.site.register(Participant)
admin.site.register(User)
admin.site.register(Request)
admin.site.register(RequestParticipant)
# Register your models here.
