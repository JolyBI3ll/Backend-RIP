from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
# Create your models here.

class NewUserManager(UserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('User must have a username')
        
        user: User = self.model(username=username, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class Participant(models.Model):
    full_name = models.CharField(max_length=50, verbose_name="ФИО")
    status = models.CharField(max_length=1, verbose_name="Статус активности",default="A") #A - active, N - inactive 
    bdate = models.DateField(verbose_name="День рождения")
    height = models.CharField(max_length=20, verbose_name="Рост")
    weight = models.CharField(max_length=20, verbose_name="Вес")
    description = models.CharField(max_length=255, verbose_name="Описание", null = True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Последнее изменение", null=True, blank=True)
    file_extension = models.CharField(max_length=10, verbose_name="Расширение файла изображения",default="jpg")

class User(AbstractBaseUser, PermissionsMixin):
    objects = NewUserManager()
    
    username = models.CharField(max_length=32, unique=True, verbose_name="Имя пользователя")
    password = models.CharField(max_length=256, verbose_name="Пароль")
    is_moderator = models.BooleanField(verbose_name="Модератор?", default=False)
    is_staff = models.BooleanField(verbose_name="Можно в админку?", default=False)
    is_superuser = models.BooleanField(verbose_name="Суперсус?", default=False)

    USERNAME_FIELD = 'username'

class Request(models.Model):
    created = models.DateTimeField(auto_now=True, verbose_name="Создание")
    send = models.DateTimeField(verbose_name="Отправка", null=True, blank=True)
    closed = models.DateTimeField(verbose_name="Закрытие", null=True, blank=True)
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