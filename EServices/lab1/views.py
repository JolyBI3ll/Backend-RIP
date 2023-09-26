from django.shortcuts import render
from datetime import date
from django.http import HttpResponse
from .models import Participant
from django.db import connection

def GetParts(request):
    data = Participant.objects.all().order_by('last_modified')
    return render(request, 'Participants.html', {'data' : {
        'participants': data
    }})

def GetPart(request, id):
    data = Participant.objects.get(pk = id)
    return render(request, 'Participant.html', {'data' : {
        'id': id,
        'participants': data
    }})

def find(request):
    data = Participant.objects.all()
    res = {'data' : {'participants' : []}}
    try:
       input = request.GET['search']
    except:
        input = ''
    for participant in data:
        if str(participant['full_name']).lower().find(input.lower()) != -1:
            res['data']['participants'].append(participant)
    return render(request, 'Participants.html', res)

def deleteFromParts(request):
    id = -1
    data = Participant.objects.all()
    if 'delete_card' in request.POST.keys():
        id = request.POST['delete_card']
    if id != -1:
        with connection.cursor() as cursor:
            cursor.execute("update lab1_participant set status = 'N' where id = " + id)
    return render(request, 'Participants.html', {'data' : {
        'id': id,
        'participants': data
    }})