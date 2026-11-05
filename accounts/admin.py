from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from .models import CustomUser

# Remove a seção de grupos nativos do Django do painel para manter a interface limpa
try:
    admin.site.unregister(DjangoGroup)
except admin.sites.NotRegistered:
    pass

# Formulário customizado para criação de usuários no admin
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'role', 'is_active')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

# Widget customizado para renderizar apenas o botão e o aviso de reconfiguração de senha
class PasswordResetLinkWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(
            '<div class="mb-2">'
            '<span class="text-muted d-block mb-2">Senhas são armazenadas com criptografia segura e não podem ser exibidas.</span>'
            '<a href="password/" class="btn btn-outline-primary btn-sm">'
            '<i class="fas fa-key me-1"></i> Reconfigurar senha'
            '</a>'
            '</div>'
        )

# Formulário de edição customizado que substitui o campo de senha padrão pelo nosso widget limpo
class CustomUserChangeForm(UserChangeForm):
    password = forms.CharField(
        label="Senha",
        required=False,
        widget=PasswordResetLinkWidget()
    )

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_list_template = 'admin/users.html'
    
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões e Perfil', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Datas', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )
    readonly_fields = ('created_at',)

    # Envia os dados de usuários em formato JSON para o gráfico
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        users_list = list(CustomUser.objects.values('created_at', 'is_active'))
        for u in users_list:
            if u['created_at']:
                u['created_at'] = u['created_at'].isoformat()
        extra_context['users_json'] = users_list
        return super().changelist_view(request, extra_context=extra_context)