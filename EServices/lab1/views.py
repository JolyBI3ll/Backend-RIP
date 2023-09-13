from django.shortcuts import render
from datetime import date
# Create your views here.
from django.http import HttpResponse


def GetData():
    return {
        'data' : {
            'participants' : [
                {'title' : 'Теряева Ксения Владимировна','BDate' : '23.06.2003', 'img' : 'images/MAN.jpg', 'id' : 1},
                {'title' : 'Малютин Илья Дмитриевич','BDate' : '19.06.2003', 'img' : 'images/MAN2.jpg', 'id' : 2},
                {'title' : 'Угрюмов Михаил Андреевич','BDate' : '13.06.2003', 'img' : 'images/MAN3.jpg', 'id' : 3},
            ]
        }
    }

data = GetData()

def GetParts(request):
    return render(request, 'Participants.html', data)

def GetPart(request, id):
    data = GetData()
    result = {}
    for participant in data['data']['participants']:
        if participant['id'] == id:
            result = participant
    return render(request, 'Participant.html', {'data' : {
        'id': id,
        'participants': result
    }})

def find(request):
    data = GetData()
    res = {'data' : {'participants' : []}}
    try:
       input = request.GET['search']
    except:
        input = ''
    for participant in data['data']['participants']:
        if str(participant['title']).lower().find(input.lower()) != -1:
            res['data']['participants'].append(participant)
    return render(request, 'Participants.html', res)