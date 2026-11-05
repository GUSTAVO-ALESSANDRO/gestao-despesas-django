from django.contrib import admin
from .models import Group, GroupMembership, Expense, ExpenseSplit
from .filters import AmountRangeFilter, AmountOwedRangeFilter, SettlementStatusFilter, HasExpensesFilter, MemberCountFilter

# Configuração da classe de administração para o modelo Group
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    change_list_template = 'admin/groups.html'
    list_display = ('name', 'description', 'invite_code', 'created_by', 'is_active', 'created_at')
    search_fields = ('name', 'invite_code', 'description')
    list_filter = ('is_active', HasExpensesFilter, MemberCountFilter, 'created_by', 'created_at')
    readonly_fields = ('created_at',)

    # Sobrescreve a view da lista para injetar dados em formato JSON no contexto adicional
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        groups_list = list(Group.objects.values('created_at', 'is_active'))
        for g in groups_list:
            if g['created_at']:
                g['created_at'] = g['created_at'].isoformat()
        extra_context['groups_json'] = groups_list
        return super().changelist_view(request, extra_context=extra_context)


# Configuração da classe de administração para o modelo GroupMembership
@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    change_list_template = 'admin/groupmembership.html'
    list_display = ('user', 'group', 'is_group_admin', 'is_accepted', 'joined_at')
    list_filter = ('is_group_admin', 'is_accepted', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)

    # Filtra o queryset com base no parâmetro 'group_id' recebido via requisição GET
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        group_id = request.GET.get('group_id')
        if group_id and group_id.isdigit():
            qs = qs.filter(group_id=int(group_id))
        return qs

    # Sobrescreve a view da lista para adicionar grupos e contadores estatísticos ao contexto
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['all_groups'] = Group.objects.all()
        
        selected = request.GET.get('group_id', '')
        extra_context['selected_group'] = int(selected) if selected.isdigit() else ''

        qs = self.get_queryset(request)
        extra_context['accepted_members'] = qs.filter(is_accepted=True).count()
        extra_context['pending_members'] = qs.filter(is_accepted=False).count()
        return super().changelist_view(request, extra_context=extra_context)


# Configuração da classe de administração para o modelo Expense
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    change_list_template = 'admin/expense.html'
    list_display = ('title', 'group', 'paid_by', 'created_by', 'amount', 'date', 'created_at')
    list_filter = (AmountRangeFilter, SettlementStatusFilter, 'group', 'paid_by', 'date', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)

    # Sobrescreve a view da lista para injetar as despesas em formato JSON no contexto adicional
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        expenses_list = list(Expense.objects.values('created_at'))
        for e in expenses_list:
            if e['created_at']:
                e['created_at'] = e['created_at'].isoformat()
        extra_context['expenses_json'] = expenses_list
        return super().changelist_view(request, extra_context=extra_context)


# Configuração da classe de administração para o modelo ExpenseSplit
@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    change_list_template = 'admin/expensesplit.html'
    list_display = ('expense', 'user', 'amount_owed', 'is_paid')
    list_filter = ('is_paid', AmountOwedRangeFilter, 'expense__group', 'user')
    search_fields = ('expense__title', 'user__username')

    # Filtra o queryset com base no parâmetro 'expense_id' recebido via requisição GET
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        expense_id = request.GET.get('expense_id')
        if expense_id and expense_id.isdigit():
            qs = qs.filter(expense_id=int(expense_id))
        return qs

    # Sobrescreve a view da lista para adicionar despesas e contadores de divisão ao contexto
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['all_expenses'] = Expense.objects.all()
        
        selected = request.GET.get('expense_id', '')
        extra_context['selected_expense'] = int(selected) if selected.isdigit() else ''

        qs = self.get_queryset(request)
        extra_context['paid_splits'] = qs.filter(is_paid=True).count()
        extra_context['unpaid_splits'] = qs.filter(is_paid=False).count()
        return super().changelist_view(request, extra_context=extra_context)