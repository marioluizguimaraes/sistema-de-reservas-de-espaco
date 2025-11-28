from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Sala, Reserva

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('cpf', 'celular', 'foto_url')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('cpf', 'celular', 'foto_url', 'email')}),
    )

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'dono', 'cidade', 'preco_por_hora', 'disponivel')
    search_fields = ('nome', 'cidade')
    list_filter = ('disponivel', 'estado')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'sala', 'solicitante', 'status', 'data_inicio', 'valor_total')
    list_filter = ('status', 'forma_pagamento')