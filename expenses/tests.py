from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib import admin
from django.test import RequestFactory
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
        membership = GroupMembership.objects.get(group=group, user=self.user)
        self.assertTrue(membership.is_accepted)
        self.assertTrue(membership.is_group_admin)

    def test_atualizar_criador_associa_novo_criador_sem_remover_dados_existentes(self):
        new_creator = CustomUser.objects.create_user(username='novo_criador', password='senha-forte-123')
        group = Group.objects.create(name='Viagem', created_by=self.user)
        group.created_by = new_creator
        group.save()

        membership = GroupMembership.objects.get(group=group, user=new_creator)
        self.assertTrue(membership.is_accepted)
        self.assertTrue(membership.is_group_admin)
        self.assertTrue(GroupMembership.objects.filter(group=group, user=self.user).exists())

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
        invited_user = CustomUser.objects.create_user(username='convidado', password='senha-forte-123')
        GroupMembership.objects.create(user=invited_user, group=self.group)
        with self.assertRaises(IntegrityError), transaction.atomic():
            GroupMembership.objects.create(user=invited_user, group=self.group)

    def test_membro_nao_aceito_por_padrao(self):
        user = CustomUser.objects.create_user(username='convidado', password='senha-forte-123')
        membership = GroupMembership.objects.create(user=user, group=self.group)
        self.assertFalse(membership.is_accepted)
        self.assertFalse(membership.is_group_admin)

    def test_membro_pendente_nao_pode_ser_administrador(self):
        user = CustomUser.objects.create_user(username='pendente', password='senha-forte-123')
        membership = GroupMembership(user=user, group=self.group, is_group_admin=True, is_accepted=False)
        with self.assertRaises(ValidationError):
            membership.full_clean()
        with self.assertRaises(ValidationError):
            membership.save()

    def test_criador_nao_pode_ser_removido_de_seu_vinculo_administrativo(self):
        membership = GroupMembership.objects.get(user=self.user, group=self.group)
        membership.is_accepted = False
        with self.assertRaises(ValidationError):
            membership.save()


class ExpenseModelTests(TestCase):
    def setUp(self):
        self.payer = CustomUser.objects.create_user(username='gustavo', password='senha-forte-123')
        self.debtor = CustomUser.objects.create_user(username='diego', password='senha-forte-123')
        self.group = Group.objects.create(name='Churrasco', created_by=self.payer)
        GroupMembership.objects.create(user=self.debtor, group=self.group, is_accepted=True)
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
            self.expense.save()

    def test_pagador_e_cadastrador_precisam_ser_membros_aceitos(self):
        outsider = CustomUser.objects.create_user(username='externo', password='senha-forte-123')
        for field in ('paid_by', 'created_by'):
            expense = Expense.objects.get(pk=self.expense.pk)
            setattr(expense, field, outsider)
            with self.subTest(field=field), self.assertRaises(ValidationError):
                expense.save()

    def test_alteracao_do_grupo_nao_pode_manter_pagador_externo(self):
        other_group = Group.objects.create(name='Outro', created_by=self.debtor)
        self.expense.group = other_group
        with self.assertRaises(ValidationError):
            self.expense.save()

    def test_rejeita_divisao_para_membro_pendente_ou_externo(self):
        outsider = CustomUser.objects.create_user(username='externo', password='senha-forte-123')
        split = ExpenseSplit(expense=self.expense, user=outsider, amount_owed=Decimal('10.00'))
        with self.assertRaises(ValidationError):
            split.save()

        pending = CustomUser.objects.create_user(username='pendente', password='senha-forte-123')
        GroupMembership.objects.create(user=pending, group=self.group)
        split.user = pending
        with self.assertRaises(ValidationError):
            split.save()

    def test_rejeita_valor_de_divisao_nao_positivo(self):
        split = ExpenseSplit(expense=self.expense, user=self.debtor, amount_owed=Decimal('0.00'))
        with self.assertRaises(ValidationError):
            split.save()

    def test_admin_formulario_de_despesa_rejeita_pagador_externo(self):
        outsider = CustomUser.objects.create_user(username='externo', password='senha-forte-123')
        request = RequestFactory().get('/admin/expenses/expense/add/')
        request.user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='admin'
        )
        model_admin = admin.site._registry[Expense]
        form_class = model_admin.get_form(request)
        form = form_class(data={
            'group': self.group.pk,
            'paid_by': outsider.pk,
            'created_by': self.payer.pk,
            'title': 'Compra',
            'description': '',
            'amount': '25.00',
            'date': '2026-11-01',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('paid_by', form.errors)

    def test_admin_inline_rejeita_divisao_de_participante_externo(self):
        from .admin import ExpenseSplitInline

        outsider = CustomUser.objects.create_user(username='externo', password='senha-forte-123')
        request = RequestFactory().get(f'/admin/expenses/expense/{self.expense.pk}/change/')
        request.user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='admin'
        )
        inline = ExpenseSplitInline(Expense, admin.site)
        formset_class = inline.get_formset(request, self.expense)
        formset = formset_class(data={
            'splits-TOTAL_FORMS': '1',
            'splits-INITIAL_FORMS': '0',
            'splits-MIN_NUM_FORMS': '0',
            'splits-MAX_NUM_FORMS': '1000',
            'splits-0-user': outsider.pk,
            'splits-0-amount_owed': '10.00',
            'splits-0-is_paid': '',
        }, instance=self.expense)
        self.assertFalse(formset.is_valid())
        self.assertIn('user', formset.forms[0].errors)

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
