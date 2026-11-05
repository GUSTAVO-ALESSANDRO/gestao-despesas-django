from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import CustomUser
from .models import Group, GroupMembership, Expense, ExpenseSplit


class GroupModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='gustavo', password='senha-forte-123')

    def test_gera_codigo_de_convite_automaticamente(self):
        group = Group.objects.create(name='Viagem', created_by=self.user)
        self.assertEqual(len(group.invite_code), 6)
        self.assertTrue(group.invite_code.isalnum())

    def test_mantem_codigo_de_convite_informado(self):
        group = Group.objects.create(name='Viagem', created_by=self.user, invite_code='RJ2026')
        self.assertEqual(group.invite_code, 'RJ2026')

    def test_codigos_gerados_sao_unicos(self):
        codes = {Group.objects.create(name=f'Grupo {i}', created_by=self.user).invite_code for i in range(20)}
        self.assertEqual(len(codes), 20)


class GroupMembershipModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='gustavo', password='senha-forte-123')
        self.group = Group.objects.create(name='República', created_by=self.user)

    def test_impede_membro_duplicado_no_mesmo_grupo(self):
        GroupMembership.objects.create(user=self.user, group=self.group)
        with self.assertRaises(IntegrityError), transaction.atomic():
            GroupMembership.objects.create(user=self.user, group=self.group)

    def test_membro_nao_aceito_por_padrao(self):
        membership = GroupMembership.objects.create(user=self.user, group=self.group)
        self.assertFalse(membership.is_accepted)
        self.assertFalse(membership.is_group_admin)


class ExpenseModelTests(TestCase):
    def setUp(self):
        self.payer = CustomUser.objects.create_user(username='gustavo', password='senha-forte-123')
        self.debtor = CustomUser.objects.create_user(username='diego', password='senha-forte-123')
        self.group = Group.objects.create(name='Churrasco', created_by=self.payer)
        self.expense = Expense.objects.create(
            group=self.group,
            paid_by=self.payer,
            created_by=self.payer,
            title='Carnes',
            amount=Decimal('150.00'),
            date=date(2026, 11, 1),
        )

    def test_representacao_textual(self):
        self.assertEqual(str(self.expense), 'Carnes - R$ 150.00')

    def test_rejeita_valor_nao_positivo(self):
        self.expense.amount = Decimal('0.00')
        with self.assertRaises(ValidationError):
            self.expense.full_clean()

    def test_impede_divisao_duplicada_para_o_mesmo_usuario(self):
        ExpenseSplit.objects.create(expense=self.expense, user=self.debtor, amount_owed=Decimal('75.00'))
        with self.assertRaises(IntegrityError), transaction.atomic():
            ExpenseSplit.objects.create(expense=self.expense, user=self.debtor, amount_owed=Decimal('75.00'))

    def test_exclusao_da_despesa_remove_divisoes(self):
        ExpenseSplit.objects.create(expense=self.expense, user=self.debtor, amount_owed=Decimal('75.00'))
        self.expense.delete()
        self.assertFalse(ExpenseSplit.objects.exists())


class AdminFiltersTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(username='admin', email='admin@split.com', password='admin', role='ADMIN')
        self.user = CustomUser.objects.create_user(username='gustavo', password='senha-forte-123')
        self.group = Group.objects.create(name='Supermercado', created_by=self.user)
        GroupMembership.objects.create(user=self.user, group=self.group, is_accepted=True)
        self.cheap = Expense.objects.create(group=self.group, paid_by=self.user, created_by=self.user, title='Pão', amount=Decimal('20.00'), date=date(2026, 11, 1))
        self.expensive = Expense.objects.create(group=self.group, paid_by=self.user, created_by=self.user, title='Compra do mês', amount=Decimal('450.00'), date=date(2026, 11, 2))
        ExpenseSplit.objects.create(expense=self.expensive, user=self.user, amount_owed=Decimal('450.00'), is_paid=True)
        self.client.force_login(self.admin)

    def results(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return list(response.context['cl'].result_list)

    def test_filtro_faixa_de_valor(self):
        self.assertEqual(self.results('/admin/expenses/expense/?faixa_valor=ate_50'), [self.cheap])
        self.assertEqual(self.results('/admin/expenses/expense/?faixa_valor=acima_200'), [self.expensive])

    def test_filtro_situacao_da_divisao(self):
        self.assertEqual(self.results('/admin/expenses/expense/?situacao=quitada'), [self.expensive])
        self.assertEqual(self.results('/admin/expenses/expense/?situacao=sem_divisao'), [self.cheap])
        self.assertEqual(self.results('/admin/expenses/expense/?situacao=pendente'), [])

    def test_filtro_grupo_possui_despesas(self):
        empty_group = Group.objects.create(name='Vazio', created_by=self.user)
        self.assertEqual(self.results('/admin/expenses/group/?possui_despesas=sim'), [self.group])
        self.assertEqual(self.results('/admin/expenses/group/?possui_despesas=nao'), [empty_group])

    def test_filtro_participacao_em_grupos(self):
        self.assertEqual(self.results('/admin/accounts/customuser/?participa_grupos=sim'), [self.user])
        self.assertEqual(self.results('/admin/accounts/customuser/?participa_grupos=nao'), [self.admin])
