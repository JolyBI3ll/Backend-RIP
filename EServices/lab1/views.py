from django.shortcuts import render
from datetime import date
# Create your views here.
from django.http import HttpResponse

def hello(request):
    return render(request, 'index.html', { 'data' : {'current_date': date.today(), 'list': ['python', 'django', 'html']}})

def GetOrders(request):
    return render(request, 'orders.html', {'data' : {'current_date': date.today(),'orders': [
            {'title': 'Книга с картинками', 'id': 1},
            {'title': 'Бутылка с водой', 'id': 2},
            {'title': 'Коврик для мышки', 'id': 3},
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