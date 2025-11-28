from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    cpf = models.CharField(max_length=14, unique=True)
    celular = models.CharField(max_length=20)
    foto_url = models.URLField(max_length=500, blank=True, null=True)
    
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username