from django.shortcuts import render
from datetime import date
# Create your views here.
from django.http import HttpResponse

def hello(request):
    return render(request, 'index.html', { 'data' : {'current_date': date.today(), 'list': ['python', 'django', 'html']}})

def GetOrders(request):
    return render(request, 'orders.html', {'data' : {'current_date': date.today(),'orders': [
            {'title': 'Участник №1', 'description': 'Описание №1', 'srcIMG': '../static/images/MAN.jpg','id': 1},
            {'title': 'Участник №2', 'description': 'Описание №2', 'srcIMG': '../static/images/MAN2.jpg','id': 2},
            {'title': 'Участник №3', 'description': 'Описание №3', 'srcIMG': '../static/images/MAN3.jpg','id': 3},
            ]
    }})

def GetOrder(request, id):
    return render(request, 'order.html', {'data' : {
        'current_date': date.today(),
        'id': id
    }})

def sendText(request, id):
    input_text = request.POST['text']
    return HttpResponse(input_text)