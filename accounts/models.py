from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Atributos personalizados além dos nativos (username, email, password, first_name, last_name)
    role = models.CharField(
        "Perfil / Papel", 
        max_length=20, 
        choices=[('ADMIN', 'Administrador'), ('USER', 'Usuário Comum')], 
        default='USER'
    )
    is_active = models.BooleanField("Ativo", default=True) # Para exclusão lógica
    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)

    class Meta(AbstractUser.Meta):
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.role})"