from django.test import TestCase

from .admin import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class CustomUserModelTests(TestCase):
    def test_usuario_comum_por_padrao(self):
        user = CustomUser.objects.create_user(username='diego', password='senha-forte-123')
        self.assertEqual(user.role, 'USER')
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.created_at)

    def test_senha_armazenada_com_hash(self):
        user = CustomUser.objects.create_user(username='diego', password='senha-forte-123')
        self.assertNotEqual(user.password, 'senha-forte-123')
        self.assertTrue(user.check_password('senha-forte-123'))

    def test_representacao_textual_inclui_perfil(self):
        user = CustomUser.objects.create_user(username='admin', password='admin', role='ADMIN')
        self.assertEqual(str(user), 'admin (ADMIN)')


class AdminAccessTests(TestCase):
    def test_admin_exige_autenticacao(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_usuario_comum_nao_acessa_admin(self):
        CustomUser.objects.create_user(username='diego', password='senha-forte-123')
        self.client.login(username='diego', password='senha-forte-123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)

    def test_superusuario_acessa_listagem_de_usuarios(self):
        admin = CustomUser.objects.create_superuser(username='admin', email='admin@split.com', password='admin')
        self.client.force_login(admin)
        response = self.client.get('/admin/accounts/customuser/')
        self.assertEqual(response.status_code, 200)

    def test_grafico_usuarios_reflete_queryset_filtrado(self):
        admin = CustomUser.objects.create_superuser(
            username='admin', email='admin@split.com', password='admin', role='ADMIN'
        )
        CustomUser.objects.create_user(username='comum', password='senha-forte-123', role='USER')
        self.client.force_login(admin)

        response = self.client.get('/admin/accounts/customuser/?role__exact=ADMIN')
        self.assertEqual(response.status_code, 200)
        chart_records = response.context['users_json']
        self.assertEqual(len(chart_records), response.context['cl'].queryset.count())
        self.assertEqual(len(chart_records), 1)
        self.assertEqual(set(chart_records[0]), {'created_at'})
        self.assertRegex(chart_records[0]['created_at'], r'^\d{4}-\d{2}-\d{2}$')

        unfiltered = self.client.get('/admin/accounts/customuser/')
        self.assertEqual(len(unfiltered.context['users_json']), unfiltered.context['cl'].queryset.count())
        self.assertEqual(len(unfiltered.context['users_json']), 2)

    def test_formulario_admin_cria_usuario_com_senha_hash_e_perfil_consistente(self):
        form = CustomUserCreationForm(data={
            'username': 'operador',
            'first_name': 'Opera',
            'last_name': 'Dor',
            'email': 'operador@example.com',
            'password': 'senha-forte-123',
            'role': 'ADMIN',
            'is_active': True,
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertNotEqual(user.password, 'senha-forte-123')
        self.assertTrue(user.check_password('senha-forte-123'))
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_formulario_admin_cria_usuario_comum_sem_acesso_staff(self):
        form = CustomUserCreationForm(data={
            'username': 'comum',
            'password': 'senha-forte-123',
            'role': 'USER',
            'is_active': True,
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superusuario_consegue_criar_usuario_pela_tela_admin(self):
        admin = CustomUser.objects.create_superuser(username='admin', email='admin@split.com', password='admin')
        self.client.force_login(admin)
        response = self.client.post('/admin/accounts/customuser/add/', {
            'username': 'novo',
            'first_name': 'Novo',
            'last_name': 'Usuario',
            'email': 'novo@example.com',
            'password': 'senha-forte-123',
            'role': 'USER',
            'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302, response.content.decode())
        created = CustomUser.objects.get(username='novo')
        self.assertTrue(created.check_password('senha-forte-123'))
        self.assertFalse(created.is_staff)

    def test_formulario_edicao_preserva_senha_existente(self):
        user = CustomUser.objects.create_user(username='editar', password='senha-forte-123')
        original_hash = user.password
        form = CustomUserChangeForm(instance=user, data={
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password': '',
            'role': 'USER',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        })
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertEqual(updated.password, original_hash)
        self.assertTrue(updated.check_password('senha-forte-123'))

    def test_role_admin_concede_staff_sem_promover_superusuario(self):
        user = CustomUser.objects.create_user(username='staff', password='senha-forte-123', role='USER')
        form = CustomUserChangeForm(instance=user, data={
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password': '',
            'role': 'ADMIN',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        })
        self.assertTrue(form.is_valid(), form.errors)
        updated = form.save()
        self.assertTrue(updated.is_staff)
        self.assertFalse(updated.is_superuser)

    def test_staff_sem_permissoes_nao_acessa_listagem_de_usuarios(self):
        staff = CustomUser.objects.create_user(
            username='staff', password='senha-forte-123', role='ADMIN', is_staff=True
        )
        self.client.force_login(staff)
        response = self.client.get('/admin/accounts/customuser/')
        self.assertEqual(response.status_code, 403)
