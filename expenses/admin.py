from django.contrib import admin
from .models import Group, GroupMembership, Expense, ExpenseSplit

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'invite_code', 'created_by', 'is_active', 'created_at')
    search_fields = ('name', 'invite_code', 'description')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'is_group_admin', 'is_accepted', 'joined_at')
    list_filter = ('is_group_admin', 'is_accepted', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'paid_by', 'created_by', 'amount', 'date', 'created_at')
    list_filter = ('date', 'group', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)

@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense', 'user', 'amount_owed', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('expense__title', 'user__username')