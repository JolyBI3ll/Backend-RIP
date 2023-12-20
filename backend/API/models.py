from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
# Create your models here.

class NewUserManager(UserManager):
    def create_user(self, username, password, **extra_fields):
        user: User = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class Participant(models.Model):
    full_name = models.CharField(max_length=50, verbose_name="ФИО")
    status = models.CharField(max_length=1, verbose_name="Статус активности",default="A") #A - active, N - inactive 
    bdate = models.DateField(verbose_name="День рождения")
    height = models.IntegerField(verbose_name="Рост")
    weight = models.IntegerField(verbose_name="Вес")
    description = models.CharField(max_length=255, verbose_name="Описание", null = True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Последнее изменение", null=True, blank=True)
    file_extension = models.CharField(max_length=10, verbose_name="Расширение файла изображения",default="jpg")

    def __str__(self):
        return self.full_name

class User(AbstractBaseUser, PermissionsMixin):
    objects = NewUserManager()
    
    username = models.CharField(max_length=32, unique=True, verbose_name="Имя пользователя")
    password = models.CharField(max_length=256, verbose_name="Пароль")
    is_moderator = models.BooleanField(verbose_name="Модератор?", default=False)
    is_staff = models.BooleanField(verbose_name="Можно в админку?", default=False)
    is_superuser = models.BooleanField(verbose_name="Суперсус?", default=False)
    is_active = models.BooleanField(verbose_name="Активный?", default=True)
    
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

class Request(models.Model):
    created = models.DateTimeField(auto_now=True, verbose_name="Создание")
    send = models.DateTimeField(verbose_name="Отправка", null=True, blank=True)
    closed = models.DateTimeField(verbose_name="Закрытие", null=True, blank=True)
    eventstatus = models.CharField(max_length=1, verbose_name = "Статус спортивного мероприятия", default = "N") #F - Fail, W - Win, #N - Non Played
    status = models.CharField(max_length=1, verbose_name="Статус", default = "I") # I - inputing, P - processing, D - deleted by user, A - success, W - fail
    user_id = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name="ID_Пользователь", related_name='user_id')
    moder_id = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name="ID_Модератор", related_name='moder_id')

# I --- P --- A
#  \     \
#   \     \
#    D     W
#
# I - created
# P - created, send
# D - created, send
# A - created, send, closed
# W - created, send, closed

class RequestParticipant(models.Model):
    is_capitan = models.BooleanField(verbose_name="Капитан?", default=False)
    Request = models.ForeignKey(Request, on_delete = models.CASCADE, verbose_name="Заявка")
    Participant = models.ForeignKey(Participant, on_delete = models.CASCADE, verbose_name="Участник")


    class Meta:
        unique_together = (('Participant', 'Request'),)