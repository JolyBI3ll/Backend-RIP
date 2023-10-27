"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api.views.ParticipantsViews import *
from api.views.RequestViews import *
from api.views.RequestParticipantViews import *
router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),

    path(r'participants/', process_Participantlist, name='participants-process'),
    path(r'participants/<int:pk>/', procces_Participant_detail, name='participants-detail-process'),

    path(r'mm/', process_MM, name = 'links'),
    
    path(r'application/', process_RequestList, name='request-list-process'),
    path(r'application/<int:pk>/', process_Request_detail, name='request-detail-process'),

    path(r'application/user/<int:user>/send/', sendRequest, name='send-request'),
    path(r'application/user/<int:user>/delete/', deleteRequest, name='request-delete'),
    path(r'application/<int:key>/close/', closeRequest, name='close-request'),
]