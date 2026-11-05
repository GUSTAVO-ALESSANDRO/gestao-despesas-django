from decimal import Decimal

from django.contrib import admin
from django.db.models import Count, Q


# Filtro base que separa registros em faixas de valor monetário
class AmountRangeFilter(admin.SimpleListFilter):
    title = "Faixa de valor"
    parameter_name = "faixa_valor"
    amount_field = "amount"

    def lookups(self, request, model_admin):
        return (
            ("ate_50", "Até R$ 50,00"),
            ("50_200", "De R$ 50,00 a R$ 200,00"),
            ("acima_200", "Acima de R$ 200,00"),
        )

    def queryset(self, request, queryset):
        field = self.amount_field
        if self.value() == "ate_50":
            return queryset.filter(**{f"{field}__lte": Decimal("50")})
        if self.value() == "50_200":
            return queryset.filter(**{f"{field}__gt": Decimal("50"), f"{field}__lte": Decimal("200")})
        if self.value() == "acima_200":
            return queryset.filter(**{f"{field}__gt": Decimal("200")})
        return queryset


# Mesma lógica de faixas aplicada ao valor devido de cada divisão
class AmountOwedRangeFilter(AmountRangeFilter):
    title = "Faixa de valor devido"
    parameter_name = "faixa_valor_devido"
    amount_field = "amount_owed"


# Classifica as despesas de acordo com a quitação das suas divisões
class SettlementStatusFilter(admin.SimpleListFilter):
    title = "Situação da divisão"
    parameter_name = "situacao"

    def lookups(self, request, model_admin):
        return (
            ("quitada", "Totalmente quitada"),
            ("pendente", "Com pendências"),
            ("sem_divisao", "Sem divisão cadastrada"),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            total_splits=Count("splits"),
            unpaid_splits=Count("splits", filter=Q(splits__is_paid=False)),
        )
        if self.value() == "quitada":
            return queryset.filter(total_splits__gt=0, unpaid_splits=0)
        if self.value() == "pendente":
            return queryset.filter(unpaid_splits__gt=0)
        if self.value() == "sem_divisao":
            return queryset.filter(total_splits=0)
        return queryset


# Separa os grupos que já possuem despesas lançadas dos que ainda estão vazios
class HasExpensesFilter(admin.SimpleListFilter):
    title = "Possui despesas"
    parameter_name = "possui_despesas"

    def lookups(self, request, model_admin):
        return (
            ("sim", "Sim"),
            ("nao", "Não"),
        )

    def queryset(self, request, queryset):
        if self.value() == "sim":
            return queryset.filter(expenses__isnull=False).distinct()
        if self.value() == "nao":
            return queryset.filter(expenses__isnull=True)
        return queryset


# Agrupa os grupos pela quantidade de membros aceitos
class MemberCountFilter(admin.SimpleListFilter):
    title = "Quantidade de membros"
    parameter_name = "qtd_membros"

    def lookups(self, request, model_admin):
        return (
            ("1", "Apenas 1 membro"),
            ("2_3", "De 2 a 3 membros"),
            ("4_mais", "4 ou mais membros"),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            accepted_members=Count("groupmembership", filter=Q(groupmembership__is_accepted=True)),
        )
        if self.value() == "1":
            return queryset.filter(accepted_members=1)
        if self.value() == "2_3":
            return queryset.filter(accepted_members__gte=2, accepted_members__lte=3)
        if self.value() == "4_mais":
            return queryset.filter(accepted_members__gte=4)
        return queryset
