from django.contrib import admin


# Separa os usuários que participam de algum grupo dos que ainda não ingressaram em nenhum
class GroupParticipationFilter(admin.SimpleListFilter):
    title = "Participa de grupos"
    parameter_name = "participa_grupos"

    def lookups(self, request, model_admin):
        return (
            ("sim", "Sim"),
            ("nao", "Não"),
        )

    def queryset(self, request, queryset):
        if self.value() == "sim":
            return queryset.filter(groupmembership__is_accepted=True).distinct()
        if self.value() == "nao":
            return queryset.exclude(groupmembership__is_accepted=True)
        return queryset
