from django.db import models
from django.conf import settings

class Group(models.Model):
    name = models.CharField("Nome do Grupo", max_length=255)
    description = models.TextField("Descrição", blank=True, null=True)
    invite_code = models.CharField("Código de Convite", max_length=10, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_groups")
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_group_admin = models.BooleanField("Admin do Grupo", default=False)
    is_accepted = models.BooleanField("Aceito no Grupo", default=False)
    joined_at = models.DateTimeField("Entrada em", auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} em {self.group.name}"

class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses")
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="paid_expenses")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_expenses")
    title = models.CharField("Título", max_length=255)
    description = models.TextField("Descrição", blank=True, null=True)
    amount = models.DecimalField("Valor Total", max_digits=10, decimal_places=2)
    date = models.DateField("Data do Gasto")
    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)

    def __str__(self):
        return f"{self.title} - R$ {self.amount}"

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="splits")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_owed = models.DecimalField("Valor Devido", max_digits=10, decimal_places=2)
    is_paid = models.BooleanField("Quitado", default=False)

    def __str__(self):
        return f"{self.user.username} deve R$ {self.amount_owed}"