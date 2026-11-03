from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Remove a seção "Autenticação e Autorização" (Grupos nativos do Django) do Admin
try:
    admin.site.unregister(DjangoGroup)
except admin.sites.NotRegistered:
    pass

# Formulário customizado para ADICIONAR usuário contemplando todos os atributos do Mermaid
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        help_text="Digite a senha para a conta."
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'role', 'is_active')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    
    # Atributos exibidos na listagem principal (tabela)
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Campos organizados na tela de EDIÇÃO de usuário
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissões e Perfil do Sistema', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )

    # Campos organizados na tela de CRIAÇÃO (Adicionar usuário)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password', 'role', 'is_active'),
        }),
    )
    
    readonly_fields = ('created_at',)