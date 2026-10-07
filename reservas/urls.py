"""
Mapeamento de Rotas (URLs) - Camada de Servidor
Porto do Itaqui - Sistema COSEG Mobilidade (PBL 1)

Define todos os endpoints HTTP do servidor em conformidade com o documento do PBL.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Documentação e Apresentação do Servidor
    path('', views.index_api_view, name='index_api'),

    # Endpoints de Veículos (Frota do COSEG)
    path('veiculos/', views.veiculos_view, name='veiculos_lista_criar'),
    path('veiculos/<str:codigo_ou_id>/', views.veiculo_detalhe_view, name='veiculo_detalhe'),

    # Endpoints de Reservas (CRUD Completo e Anticonflito)
    path('reservas/', views.reservas_view, name='reservas_lista_criar'),
    path('reservas/<int:reserva_id>/', views.reserva_detalhe_view, name='reserva_detalhe_atualizar_deletar'),
    path('reservas/verificar-conflito/', views.verificar_conflito_view, name='verificar_conflito'),
]
