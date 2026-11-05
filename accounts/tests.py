from django.test import TestCase

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
