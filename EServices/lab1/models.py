from django.db import models
# Create your models here.
class Participant(models.Model):
    full_name = models.CharField(max_length=50, verbose_name="ФИО")
    link = models.CharField(max_length=50, verbose_name="Ссылка на изображение", null = True, blank=True)
    status = models.CharField(max_length=1, verbose_name="Статус активности") #A - active, N - inactive 
    bdate = models.DateField(verbose_name="День рождения")
    height = models.CharField(max_length=20, verbose_name="Рост")
    weight = models.CharField(max_length=20, verbose_name="Вес")
    description = models.CharField(max_length=255, verbose_name="Описание", null = True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Последнее изменение", null=True, blank=True)

class User(models.Model):
    name = models.CharField(max_length=20, verbose_name="Имя")
    login = models.CharField(max_length=20, verbose_name="Логин")
    password = models.CharField(max_length=50, verbose_name="Пароль")
    is_manager = models.BooleanField(default = False)

class Request(models.Model):
    created = models.DateTimeField(auto_now=True, verbose_name="Создание")
    send = models.DateTimeField(verbose_name="Отправка")
    closed = models.DateTimeField(verbose_name="Закрытие")
    status = models.CharField(max_length=20, verbose_name="Статус") # I - inputing, P - processing, D - deleted by user, A - success, W - fail
    user_id = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name="ID_Пользователь", related_name='user_id')
    moder_id = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name="ID_Модератор", related_name='moder_id')

class RequestParticipant(models.Model):
    Participant = models.ForeignKey(Participant, on_delete = models.CASCADE, verbose_name="Участник")
    Request = models.ForeignKey(Request, on_delete = models.CASCADE, verbose_name="Заявка")