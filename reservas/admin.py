"""
Configuração do Django Admin - Sistema COSEG Mobilidade
Porto do Itaqui - Programação para Web (PBL 1)
"""

from django.contrib import admin
from .models import Veiculo, Reserva


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'modelo', 'categoria', 'capacidade', 'placa', 'ativo')
    list_filter = ('categoria', 'ativo')
    search_fields = ('codigo', 'modelo', 'placa')
    ordering = ('codigo',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'veiculo', 'data', 'horario_saida', 'horario_retorno',
        'solicitante', 'setor', 'quantidade_passageiros', 'status'
    )
    list_filter = ('status', 'data', 'veiculo__categoria', 'veiculo')
    search_fields = ('solicitante', 'setor', 'atividade', 'origem', 'destino')
    date_hierarchy = 'data'
    ordering = ('-data', 'horario_saida')
