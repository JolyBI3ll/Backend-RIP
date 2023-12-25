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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views.authViews import *
router = routers.DefaultRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Регистрация участников на спортивное соревнование.",
      default_version='v1',
      description="Наше веб-приложение по регистрации участников на спортивное соревнование является удобным и интуитивно понятным инструментом, которым может воспользоваться любой организатор соревнований. Основная цель нашего приложения - упростить процесс регистрации для организаторов и участников, устранить бумажную волокиту и снизить время и усилия, требующиеся для проведения соревнования. ",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="asman2003pda45@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('request/<int:pk>/result/', EventStatus_View.as_view(), name = 'event-status-update'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/check/', check, name='check'),

    path(r'participants/', Participantlist_view.as_view(), name='participants-process'),
    path(r'participants/<int:pk>/', ParticipantDetail_view.as_view(), name='participants-detail-process'),

    path(r'links/', links_view.as_view(), name = 'links'),
    
    path(r'request/', requestList_view.as_view(), name='request-list-process'),
    path(r'request/current/', Current_Inp_View.as_view(), name='request-current'),
    path(r'request/<int:pk>/', requestDetail_view.as_view(), name='request-detail-process'),

    
]

