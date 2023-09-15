from django.shortcuts import render
from datetime import date
# Create your views here.
from django.http import HttpResponse


def GetData():
    return {
        'data' : {
            'participants' : [
                {'title' : 'Теряева Ксения Владимировна','BDate' : '23.06.2003','Sport' : 'Волейбол','Description' : 'Юная волейболистка, которая профессионально занимается данной спортивной дисциплиной в течение 7 лет. Неоднократно занимала призовые места в соревнованиях.','Power': '6','Agility': '8','Endurance': '9', 'img' : 'images/MAN.jpg', 'id' : 1},
                {'title' : 'Малютин Илья Дмитриевич','BDate' : '19.06.2003','Sport' : 'Футбол', 'Description' : 'Талант в мире футбола, бомбардир юношеской команды, молодая звезда футбольного небосвода, занимается футболом с 7 лет, он был рождён, чтобы вломиться в высшую лигу и обыграть любого игрока на поле.','Power': '10','Agility': '7','Endurance': '8','img' : 'images/MAN2.jpg', 'id' : 2},
                {'title' : 'Угрюмов Михаил Андреевич','BDate' : '13.06.2003','Sport' : 'Плавание','Description' : 'Пловец, профессионально занимающийся спортивным плаванием со стажем в 11 лет, он научился плавать в 1 год своей жизни, действительно удивительный человек', 'Power': '9','Agility': '5','Endurance': '10','img' : 'images/MAN3.jpg', 'id' : 3},
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