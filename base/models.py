from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator  # Добавьте этот импорт

# Create your models here.


class Task(models.Model):
    objects = None
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(3, "Название должно содержать минимум 3 символа"),
            MaxLengthValidator(100, "Название не должно превышать 100 символов")
        ]
    )
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = 'user'