import secrets
import string

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.conf import settings

INVITE_CODE_ALPHABET = string.ascii_uppercase + string.digits
INVITE_CODE_LENGTH = 6

class Group(models.Model):
    name = models.CharField("Nome do Grupo", max_length=255)
    description = models.TextField("Descrição", blank=True, null=True)
    invite_code = models.CharField("Código de Convite", max_length=10, unique=True, blank=True, help_text="Deixe em branco para gerar automaticamente.")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_groups")
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # Gera um código de convite alfanumérico único caso nenhum tenha sido informado
    @staticmethod
    def generate_invite_code():
        while True:
            code = "".join(secrets.choice(INVITE_CODE_ALPHABET) for _ in range(INVITE_CODE_LENGTH))
            if not Group.objects.filter(invite_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        with transaction.atomic():
            super().save(*args, **kwargs)
            GroupMembership.objects.update_or_create(
                group=self,
                user=self.created_by,
                defaults={'is_accepted': True, 'is_group_admin': True},
            )

class GroupMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_group_admin = models.BooleanField("Admin do Grupo", default=False)
    is_accepted = models.BooleanField("Aceito no Grupo", default=False)
    joined_at = models.DateTimeField("Entrada em", auto_now_add=True)

    class Meta:
        verbose_name = "Membro do Grupo"
        verbose_name_plural = "Membros dos Grupos"
        ordering = ['group', '-is_group_admin', 'joined_at']
        # Impede que o mesmo usuário seja vinculado mais de uma vez ao mesmo grupo
        constraints = [
            models.UniqueConstraint(fields=['user', 'group'], name='unique_membro_por_grupo'),
        ]

    def __str__(self):
        return f"{self.user.username} em {self.group.name}"

    def clean(self):
        super().clean()
        if self.is_group_admin and not self.is_accepted:
            raise ValidationError({
                'is_group_admin': 'Um membro precisa ser aceito antes de se tornar administrador do grupo.'
            })
        if (
            self.group_id and self.user_id
            and Group.objects.filter(pk=self.group_id, created_by_id=self.user_id).exists()
            and (not self.is_accepted or not self.is_group_admin)
        ):
            raise ValidationError('O criador do grupo deve permanecer como membro aceito e administrador.')

    def save(self, *args, **kwargs):
        self.full_clean(validate_unique=False, validate_constraints=False)
        super().save(*args, **kwargs)

class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="expenses")
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="paid_expenses")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_expenses")
    title = models.CharField("Título", max_length=255)
    description = models.TextField("Descrição", blank=True, null=True)
    amount = models.DecimalField("Valor Total", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    date = models.DateField("Data do Gasto")
    created_at = models.DateTimeField("Cadastrado em", auto_now_add=True)

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - R$ {self.amount}"

    def clean(self):
        super().clean()
        if not self.group_id:
            return
        for field, user_id, label in (
            ('paid_by', self.paid_by_id, 'pagador'),
            ('created_by', self.created_by_id, 'responsável pelo cadastro'),
        ):
            if user_id and not GroupMembership.objects.filter(
                group_id=self.group_id, user_id=user_id, is_accepted=True
            ).exists():
                raise ValidationError({
                    field: f'O {label} deve ser um membro aceito do grupo da despesa.'
                })

    def save(self, *args, **kwargs):
        self.full_clean(validate_unique=False, validate_constraints=False)
        super().save(*args, **kwargs)

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="splits")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_owed = models.DecimalField("Valor Devido", max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    is_paid = models.BooleanField("Quitado", default=False)

    class Meta:
        verbose_name = "Divisão de Despesa"
        verbose_name_plural = "Divisões de Despesas"
        ordering = ['expense', 'user']
        # Cada usuário possui no máximo uma fatia por despesa
        constraints = [
            models.UniqueConstraint(fields=['expense', 'user'], name='unique_divisao_por_usuario'),
        ]

    def __str__(self):
        return f"{self.user.username} deve R$ {self.amount_owed}"

    def clean(self):
        super().clean()
        if self.expense_id and self.user_id:
            if not GroupMembership.objects.filter(
                group_id=self.expense.group_id,
                user_id=self.user_id,
                is_accepted=True,
            ).exists():
                raise ValidationError({
                    'user': 'O participante deve ser um membro aceito do grupo da despesa.'
                })

    def save(self, *args, **kwargs):
        self.full_clean(validate_unique=False, validate_constraints=False)
        super().save(*args, **kwargs)
