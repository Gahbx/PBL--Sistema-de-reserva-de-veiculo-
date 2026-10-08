"""
Configuração do Django Admin - Sistema COSEG Mobilidade
Porto do Itaqui - Programação para Web (PBL 1)
"""

from django import forms
from django.contrib import admin
from .models import Veiculo, Reserva
from .services import validar_regras_reserva


class ReservaAdminForm(forms.ModelForm):
    """
    Formulário administrativo customizado para tratar todas as validações
    de forma amigável no painel, garantindo que mensagens de erro
    sejam renderizadas em caixas de aviso elegantes sem nenhum crash.
    """
    class Meta:
        model = Reserva
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        veiculo = cleaned_data.get('veiculo')
        data = cleaned_data.get('data')
        horario_saida = cleaned_data.get('horario_saida')
        horario_retorno = cleaned_data.get('horario_retorno')
        quantidade_passageiros = cleaned_data.get('quantidade_passageiros')

        # Se campos obrigatórios estiverem faltando, o Django já adicionou o erro padrão
        if not (veiculo and data and horario_saida and horario_retorno and quantidade_passageiros):
            return cleaned_data

        erros = validar_regras_reserva(
            veiculo=veiculo,
            data=data,
            horario_saida=horario_saida,
            horario_retorno=horario_retorno,
            quantidade_passageiros=quantidade_passageiros,
            reserva_id=self.instance.id if self.instance else None
        )

        for campo, msg in erros.items():
            if campo in self.fields:
                self.add_error(campo, msg)
            elif campo == 'conflito':
                # Associa o aviso de conflito ao campo veiculo e horário de saída
                self.add_error('veiculo', msg)
            else:
                self.add_error(None, msg)

        return cleaned_data


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'modelo', 'categoria', 'capacidade', 'placa', 'ativo')
    list_filter = ('categoria', 'ativo')
    search_fields = ('codigo', 'modelo', 'placa')
    ordering = ('codigo',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    form = ReservaAdminForm
    list_display = (
        'id', 'veiculo', 'data', 'horario_saida', 'horario_retorno',
        'solicitante', 'setor', 'quantidade_passageiros', 'status'
    )
    list_filter = ('status', 'data', 'veiculo__categoria', 'veiculo')
    search_fields = ('solicitante', 'setor', 'atividade', 'origem', 'destino')
    date_hierarchy = 'data'
    ordering = ('-data', 'horario_saida')


# Customização do Painel Administrativo para o COSEG
admin.site.site_header = "COSEG Mobilidade — Gestão de Frota (Porto do Itaqui)"
admin.site.site_title = "COSEG Mobilidade"
admin.site.index_title = "Administração da Frota e Reservas de Veículos"

# Oculta 'Grupos' para manter o painel limpo e focado no domínio do sistema
from django.contrib.auth.models import Group
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
