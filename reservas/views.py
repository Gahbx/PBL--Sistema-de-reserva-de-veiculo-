"""
Módulo de Views / Endpoints da Camada de Servidor - Sistema COSEG Mobilidade
Porto do Itaqui - Programação para Web (PBL 1)

Este módulo implementa os endpoints HTTP em formato JSON (API RESTful),
responsáveis por receber as requisições, orquestrar as validações de regras
de negócio com o Django ORM e retornar respostas padronizadas com status HTTP.

Todas as respostas seguem o padrão:
- Em caso de sucesso: {"sucesso": True, "mensagem": "...", "dados": {...}}
- Em caso de erro: {"sucesso": False, "mensagem": "...", "erros": {...}}
"""

import json
from datetime import datetime, date, time
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import Veiculo, Reserva, StatusReserva, CategoriaVeiculo
from .services import (
    buscar_reservas_conflitantes,
    validar_regras_reserva,
)


def _parse_body(request):
    """
    Função auxiliar para extrair dados da requisição,
    suportando tanto Content-Type: application/json quanto formulários POST padrão.
    """
    if request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return request.POST.dict()


# ==============================================================================
# ROTA INICIAL / DOCUMENTAÇÃO DOS ENDPOINTS
# ==============================================================================

def index_api_view(request):
    """
    GET /
    Retorna a apresentação da Camada de Servidor do COSEG Mobilidade
    e o catálogo de endpoints disponíveis para integração no PBL 2.
    """
    return JsonResponse({
        "sistema": "COSEG Mobilidade - Servidor de Reserva de Veículos",
        "instituicao": "Porto do Itaqui / UNDB",
        "disciplina": "Programação para Web (PBL 1 - Etapa 02)",
        "status": "Online e operacional",
        "endpoints": {
            "frota": {
                "GET /veiculos/": "Lista todos os veículos da frota e suas capacidades",
                "POST /veiculos/": "Cadastra um novo veículo na frota",
                "GET /veiculos/<codigo>/": "Detalhes de um veículo específico",
            },
            "reservas": {
                "GET /reservas/": "Lista reservas cadastradas (filtros por ?data=YYYY-MM-DD, ?veiculo=VL-01, ?status=CONFIRMADA)",
                "POST /reservas/": "Registra uma nova reserva aplicando todas as regras de negócio",
                "GET /reservas/<id>/": "Consulta detalhes de uma reserva específica",
                "PUT /reservas/<id>/": "Atualiza uma reserva existente",
                "DELETE /reservas/<id>/": "Cancela ou exclui uma reserva do banco",
                "POST /reservas/verificar-conflito/": "Verifica se há sobreposição de horário para um veículo em uma data",
            }
        }
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


# ==============================================================================
# CRUD DA FROTA DE VEÍCULOS
# ==============================================================================

@csrf_exempt
def veiculos_view(request):
    """
    GET /veiculos/  -> Lista todos os veículos cadastrados na frota.
    POST /veiculos/ -> Cadastra um novo veículo no banco de dados.
    """
    if request.method == 'GET':
        veiculos = Veiculo.objects.all().order_by('codigo')
        lista = []
        for v in veiculos:
            lista.append({
                "id": v.id,
                "codigo": v.codigo,
                "modelo": v.modelo,
                "placa": v.placa,
                "categoria": v.categoria,
                "categoria_descricao": v.get_categoria_display(),
                "capacidade_passageiros": v.capacidade,
                "ativo": v.ativo,
            })
        return JsonResponse({
            "sucesso": True,
            "total": len(lista),
            "veiculos": lista
        }, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    elif request.method == 'POST':
        dados = _parse_body(request)
        codigo = dados.get('codigo', '').strip().upper()
        modelo = dados.get('modelo', '').strip()
        placa = dados.get('placa', '').strip().upper()
        categoria = dados.get('categoria', CategoriaVeiculo.LEVE)
        capacidade = dados.get('capacidade')

        if not codigo or not modelo or capacidade is None:
            return JsonResponse({
                "sucesso": False,
                "mensagem": "Campos obrigatórios ausentes: 'codigo', 'modelo' e 'capacidade'.",
            }, status=400, json_dumps_params={'ensure_ascii': False})

        try:
            capacidade_int = int(capacidade)
            if categoria == CategoriaVeiculo.LEVE and capacidade_int > 4:
                return JsonResponse({
                    "sucesso": False,
                    "mensagem": "Veículos leves comportam no máximo 4 passageiros.",
                }, status=400, json_dumps_params={'ensure_ascii': False})
            elif categoria == CategoriaVeiculo.COLETIVO and capacidade_int > 18:
                return JsonResponse({
                    "sucesso": False,
                    "mensagem": "Veículos coletivos comportam no máximo 18 passageiros.",
                }, status=400, json_dumps_params={'ensure_ascii': False})

            veiculo = Veiculo.objects.create(
                codigo=codigo,
                modelo=modelo,
                placa=placa,
                categoria=categoria,
                capacidade=capacidade_int,
                ativo=True
            )

            return JsonResponse({
                "sucesso": True,
                "mensagem": f"Veículo {veiculo.codigo} cadastrado com sucesso!",
                "dados": {
                    "id": veiculo.id,
                    "codigo": veiculo.codigo,
                    "modelo": veiculo.modelo,
                    "categoria": veiculo.categoria,
                    "capacidade": veiculo.capacidade
                }
            }, status=201, json_dumps_params={'ensure_ascii': False, 'indent': 2})

        except Exception as erro:
            return JsonResponse({
                "sucesso": False,
                "mensagem": f"Erro ao cadastrar veículo: {str(erro)}"
            }, status=400, json_dumps_params={'ensure_ascii': False})

    return HttpResponseNotAllowed(['GET', 'POST'])


def veiculo_detalhe_view(request, codigo_ou_id):
    """
    GET /veiculos/<codigo_ou_id>/
    Retorna os detalhes de um veículo e a lista de suas reservas cadastradas.
    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    veiculo = None
    if str(codigo_ou_id).isdigit():
        veiculo = Veiculo.objects.filter(id=int(codigo_ou_id)).first()
    if not veiculo:
        veiculo = Veiculo.objects.filter(codigo__iexact=str(codigo_ou_id)).first()

    if not veiculo:
        return JsonResponse({
            "sucesso": False,
            "mensagem": f"Veículo '{codigo_ou_id}' não encontrado na frota do COSEG."
        }, status=404, json_dumps_params={'ensure_ascii': False})

    reservas = veiculo.reservas.all().order_by('-data', 'horario_saida')
    reservas_lista = [
        {
            "id": r.id,
            "data": r.data.strftime('%Y-%m-%d'),
            "horario_saida": r.horario_saida.strftime('%H:%M'),
            "horario_retorno": r.horario_retorno.strftime('%H:%M'),
            "solicitante": r.solicitante,
            "setor": r.setor,
            "atividade": r.atividade,
            "status": r.status,
        }
        for r in reservas
    ]

    return JsonResponse({
        "sucesso": True,
        "veiculo": {
            "id": veiculo.id,
            "codigo": veiculo.codigo,
            "modelo": veiculo.modelo,
            "placa": veiculo.placa,
            "categoria": veiculo.categoria,
            "categoria_descricao": veiculo.get_categoria_display(),
            "capacidade": veiculo.capacidade,
            "ativo": veiculo.ativo,
        },
        "total_reservas": len(reservas_lista),
        "reservas": reservas_lista
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


# ==============================================================================
# CRUD DAS RESERVAS DE VEÍCULOS
# ==============================================================================

@csrf_exempt
def reservas_view(request):
    """
    GET /reservas/  -> Lista reservas cadastradas (READ - R do CRUD).
    POST /reservas/ -> Registra uma nova reserva (CREATE - C do CRUD).
    """
    if request.method == 'GET':
        query = Reserva.objects.all().select_related('veiculo').order_by('-data', 'horario_saida')

        # Filtros opcionais
        data_param = request.GET.get('data')
        if data_param:
            query = query.filter(data=data_param)

        veiculo_param = request.GET.get('veiculo')
        if veiculo_param:
            if veiculo_param.isdigit():
                query = query.filter(veiculo_id=int(veiculo_param))
            else:
                query = query.filter(veiculo__codigo__iexact=veiculo_param)

        status_param = request.GET.get('status')
        if status_param:
            query = query.filter(status__iexact=status_param)

        lista = []
        for r in query:
            lista.append({
                "id": r.id,
                "solicitante": r.solicitante,
                "setor": r.setor,
                "atividade": r.atividade,
                "origem": r.origem,
                "destino": r.destino,
                "data": r.data.strftime('%Y-%m-%d'),
                "horario_saida": r.horario_saida.strftime('%H:%M'),
                "horario_retorno": r.horario_retorno.strftime('%H:%M'),
                "quantidade_passageiros": r.quantidade_passageiros,
                "veiculo": {
                    "id": r.veiculo.id,
                    "codigo": r.veiculo.codigo,
                    "modelo": r.veiculo.modelo,
                    "capacidade": r.veiculo.capacidade,
                    "categoria": r.veiculo.categoria,
                },
                "observacoes": r.observacoes or "",
                "status": r.status,
                "criado_em": r.criado_em.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return JsonResponse({
            "sucesso": True,
            "total": len(lista),
            "reservas": lista
        }, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    elif request.method == 'POST':
        dados = _parse_body(request)

        # Campos obrigatórios
        solicitante = dados.get('solicitante', '').strip()
        setor = dados.get('setor', '').strip()
        atividade = dados.get('atividade', '').strip()
        origem = dados.get('origem', '').strip()
        destino = dados.get('destino', '').strip()
        data_str = dados.get('data')
        saida_str = dados.get('horario_saida')
        retorno_str = dados.get('horario_retorno')
        qtd_pass = dados.get('quantidade_passageiros')
        veiculo_identificador = dados.get('veiculo') or dados.get('veiculo_id') or dados.get('veiculo_codigo')
        observacoes = dados.get('observacoes', '').strip()

        # Validação de presença de campos de identificação
        erros_iniciais = {}
        if not solicitante:
            erros_iniciais['solicitante'] = "O campo solicitante é obrigatório."
        if not setor:
            erros_iniciais['setor'] = "O campo setor é obrigatório."
        if not atividade:
            erros_iniciais['atividade'] = "O campo atividade é obrigatório."
        if not origem:
            erros_iniciais['origem'] = "O campo origem é obrigatório."
        if not destino:
            erros_iniciais['destino'] = "O campo destino é obrigatório."

        if erros_iniciais:
            return JsonResponse({
                "sucesso": False,
                "mensagem": "Campos obrigatórios não preenchidos.",
                "erros": erros_iniciais
            }, status=400, json_dumps_params={'ensure_ascii': False})

        # Localização do veículo
        veiculo = None
        if veiculo_identificador:
            if str(veiculo_identificador).isdigit():
                veiculo = Veiculo.objects.filter(id=int(veiculo_identificador)).first()
            else:
                veiculo = Veiculo.objects.filter(codigo__iexact=str(veiculo_identificador)).first()

        # Conversão de data e horários
        data_val = None
        saida_val = None
        retorno_val = None
        qtd_val = None

        try:
            if data_str:
                data_val = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                "sucesso": False,
                "mensagem": "Formato de data inválido. Utilize o formato AAAA-MM-DD (ex: 2026-08-18)."
            }, status=400, json_dumps_params={'ensure_ascii': False})

        try:
            if saida_str:
                saida_val = datetime.strptime(saida_str, '%H:%M').time()
        except ValueError:
            return JsonResponse({
                "sucesso": False,
                "mensagem": "Formato de horário de saída inválido. Utilize HH:MM (ex: 08:00)."
            }, status=400, json_dumps_params={'ensure_ascii': False})

        try:
            if retorno_str:
                retorno_val = datetime.strptime(retorno_str, '%H:%M').time()
        except ValueError:
            return JsonResponse({
                "sucesso": False,
                "mensagem": "Formato de horário de retorno inválido. Utilize HH:MM (ex: 10:00)."
            }, status=400, json_dumps_params={'ensure_ascii': False})

        if qtd_pass is not None:
            try:
                qtd_val = int(qtd_pass)
            except ValueError:
                return JsonResponse({
                    "sucesso": False,
                    "mensagem": "Quantidade de passageiros deve ser um número inteiro."
                }, status=400, json_dumps_params={'ensure_ascii': False})

        # Executa validações de regras de negócio
        erros_validacao = validar_regras_reserva(
            veiculo=veiculo,
            data=data_val,
            horario_saida=saida_val,
            horario_retorno=retorno_val,
            quantidade_passageiros=qtd_val,
            permitir_data_historica=False
        )

        if erros_validacao:
            return JsonResponse({
                "sucesso": False,
                "mensagem": "A solicitação viola uma ou mais regras de negócio do COSEG.",
                "erros": erros_validacao
            }, status=400, json_dumps_params={'ensure_ascii': False, 'indent': 2})

        # Persistência no banco via Django ORM
        reserva = Reserva.objects.create(
            solicitante=solicitante,
            setor=setor,
            atividade=atividade,
            origem=origem,
            destino=destino,
            data=data_val,
            horario_saida=saida_val,
            horario_retorno=retorno_val,
            quantidade_passageiros=qtd_val,
            veiculo=veiculo,
            observacoes=observacoes,
            status=StatusReserva.CONFIRMADA
        )

        return JsonResponse({
            "sucesso": True,
            "mensagem": f"Reserva #{reserva.id} confirmada com sucesso para o veículo {veiculo.codigo}!",
            "dados": {
                "id": reserva.id,
                "solicitante": reserva.solicitante,
                "veiculo": reserva.veiculo.codigo,
                "data": reserva.data.strftime('%Y-%m-%d'),
                "horario_saida": reserva.horario_saida.strftime('%H:%M'),
                "horario_retorno": reserva.horario_retorno.strftime('%H:%M'),
                "passageiros": reserva.quantidade_passageiros,
                "status": reserva.status,
            }
        }, status=201, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    return HttpResponseNotAllowed(['GET', 'POST'])


@csrf_exempt
def reserva_detalhe_view(request, reserva_id):
    """
    GET /reservas/<reserva_id>/    -> Detalhes de uma reserva (READ individual).
    PUT/PATCH /reservas/<reserva_id>/ -> Atualização de reserva (UPDATE - U do CRUD).
    DELETE /reservas/<reserva_id>/ -> Cancelamento ou exclusão (DELETE - D do CRUD).
    """
    reserva = Reserva.objects.filter(id=reserva_id).select_related('veiculo').first()
    if not reserva:
        return JsonResponse({
            "sucesso": False,
            "mensagem": f"Reserva #{reserva_id} não encontrada no banco de dados."
        }, status=404, json_dumps_params={'ensure_ascii': False})

    # READ INDIVIDUAL
    if request.method == 'GET':
        return JsonResponse({
            "sucesso": True,
            "dados": {
                "id": reserva.id,
                "solicitante": reserva.solicitante,
                "setor": reserva.setor,
                "atividade": reserva.atividade,
                "origem": reserva.origem,
                "destino": reserva.destino,
                "data": reserva.data.strftime('%Y-%m-%d'),
                "horario_saida": reserva.horario_saida.strftime('%H:%M'),
                "horario_retorno": reserva.horario_retorno.strftime('%H:%M'),
                "quantidade_passageiros": reserva.quantidade_passageiros,
                "veiculo": {
                    "id": reserva.veiculo.id,
                    "codigo": reserva.veiculo.codigo,
                    "modelo": reserva.veiculo.modelo,
                    "capacidade": reserva.veiculo.capacidade,
                    "categoria": reserva.veiculo.categoria,
                },
                "observacoes": reserva.observacoes or "",
                "status": reserva.status,
                "criado_em": reserva.criado_em.strftime('%Y-%m-%d %H:%M:%S'),
                "atualizado_em": reserva.atualizado_em.strftime('%Y-%m-%d %H:%M:%S'),
            }
        }, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    # UPDATE
    elif request.method in ['PUT', 'PATCH']:
        dados = _parse_body(request)

        # Se alterar veículo
        veiculo = reserva.veiculo
        veiculo_identificador = dados.get('veiculo') or dados.get('veiculo_id') or dados.get('veiculo_codigo')
        if veiculo_identificador:
            if str(veiculo_identificador).isdigit():
                veiculo = Veiculo.objects.filter(id=int(veiculo_identificador)).first()
            else:
                veiculo = Veiculo.objects.filter(codigo__iexact=str(veiculo_identificador)).first()

        # Parse de novos dados ou manter os existentes
        nova_data = reserva.data
        if 'data' in dados:
            try:
                nova_data = datetime.strptime(dados['data'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({"sucesso": False, "mensagem": "Data inválida."}, status=400)

        nova_saida = reserva.horario_saida
        if 'horario_saida' in dados:
            try:
                nova_saida = datetime.strptime(dados['horario_saida'], '%H:%M').time()
            except ValueError:
                return JsonResponse({"sucesso": False, "mensagem": "Horário de saída inválido."}, status=400)

        novo_retorno = reserva.horario_retorno
        if 'horario_retorno' in dados:
            try:
                novo_retorno = datetime.strptime(dados['horario_retorno'], '%H:%M').time()
            except ValueError:
                return JsonResponse({"sucesso": False, "mensagem": "Horário de retorno inválido."}, status=400)

        novos_pass = reserva.quantidade_passageiros
        if 'quantidade_passageiros' in dados:
            try:
                novos_pass = int(dados['quantidade_passageiros'])
            except ValueError:
                return JsonResponse({"sucesso": False, "mensagem": "Passageiros deve ser número inteiro."}, status=400)

        # Validação via serviços (ignora o id da própria reserva na busca por conflitos)
        erros_validacao = validar_regras_reserva(
            veiculo=veiculo,
            data=nova_data,
            horario_saida=nova_saida,
            horario_retorno=novo_retorno,
            quantidade_passageiros=novos_pass,
            reserva_id=reserva.id
        )

        if erros_validacao:
            return JsonResponse({
                "sucesso": False,
                "mensagem": "Inconsistências encontradas ao atualizar reserva.",
                "erros": erros_validacao
            }, status=400, json_dumps_params={'ensure_ascii': False, 'indent': 2})

        # Atualiza campos
        reserva.veiculo = veiculo
        reserva.data = nova_data
        reserva.horario_saida = nova_saida
        reserva.horario_retorno = novo_retorno
        reserva.quantidade_passageiros = novos_pass

        if 'solicitante' in dados: reserva.solicitante = dados['solicitante'].strip()
        if 'setor' in dados: reserva.setor = dados['setor'].strip()
        if 'atividade' in dados: reserva.atividade = dados['atividade'].strip()
        if 'origem' in dados: reserva.origem = dados['origem'].strip()
        if 'destino' in dados: reserva.destino = dados['destino'].strip()
        if 'observacoes' in dados: reserva.observacoes = dados['observacoes'].strip()
        if 'status' in dados:
            status_cand = dados['status'].upper()
            if status_cand in dict(StatusReserva.choices):
                reserva.status = status_cand

        reserva.save()

        return JsonResponse({
            "sucesso": True,
            "mensagem": f"Reserva #{reserva.id} atualizada com sucesso!",
            "dados": {
                "id": reserva.id,
                "veiculo": reserva.veiculo.codigo,
                "data": reserva.data.strftime('%Y-%m-%d'),
                "horario_saida": reserva.horario_saida.strftime('%H:%M'),
                "horario_retorno": reserva.horario_retorno.strftime('%H:%M'),
                "status": reserva.status,
            }
        }, json_dumps_params={'ensure_ascii': False, 'indent': 2})

    # DELETE
    elif request.method == 'DELETE':
        dados = _parse_body(request)
        tipo_exclusao = dados.get('tipo', 'cancelar')

        if tipo_exclusao == 'excluir':
            reserva.delete()
            return JsonResponse({
                "sucesso": True,
                "mensagem": f"Reserva #{reserva_id} excluída permanentemente do banco de dados."
            }, json_dumps_params={'ensure_ascii': False})
        else:
            reserva.status = StatusReserva.CANCELADA
            reserva.save(update_fields=['status'])
            return JsonResponse({
                "sucesso": True,
                "mensagem": f"Reserva #{reserva_id} marcada como CANCELADA no sistema COSEG."
            }, json_dumps_params={'ensure_ascii': False})

    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


# ==============================================================================
# ENDPOINT DE SIMULAÇÃO E DETECÇÃO DE CONFLITO
# ==============================================================================

@csrf_exempt
def verificar_conflito_view(request):
    """
    POST /reservas/verificar-conflito/
    Permite consultar se uma combinação de veículo, data e horários
    possui conflito com alguma reserva já confirmada.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    dados = _parse_body(request)
    veiculo_id = dados.get('veiculo') or dados.get('veiculo_id') or dados.get('veiculo_codigo')
    data_str = dados.get('data')
    saida_str = dados.get('horario_saida')
    retorno_str = dados.get('horario_retorno')
    reserva_id = dados.get('reserva_id')

    if not veiculo_id or not data_str or not saida_str or not retorno_str:
        return JsonResponse({
            "sucesso": False,
            "mensagem": "Parâmetros obrigatórios: 'veiculo', 'data', 'horario_saida', 'horario_retorno'."
        }, status=400, json_dumps_params={'ensure_ascii': False})

    veiculo = None
    if str(veiculo_id).isdigit():
        veiculo = Veiculo.objects.filter(id=int(veiculo_id)).first()
    else:
        veiculo = Veiculo.objects.filter(codigo__iexact=str(veiculo_id)).first()

    if not veiculo:
        return JsonResponse({
            "sucesso": False,
            "mensagem": f"Veículo '{veiculo_id}' não localizado."
        }, status=404, json_dumps_params={'ensure_ascii': False})

    try:
        data_val = datetime.strptime(data_str, '%Y-%m-%d').date()
        saida_val = datetime.strptime(saida_str, '%H:%M').time()
        retorno_val = datetime.strptime(retorno_str, '%H:%M').time()
    except ValueError as e:
        return JsonResponse({
            "sucesso": False,
            "mensagem": f"Erro na formatação dos campos de data/horário: {str(e)}"
        }, status=400, json_dumps_params={'ensure_ascii': False})

    # Verifica se horário de retorno é posterior ao de saída
    if retorno_val <= saida_val:
        return JsonResponse({
            "sucesso": False,
            "mensagem": f"Horário de retorno ({retorno_val.strftime('%H:%M')}) deve ser posterior ao de saída ({saida_val.strftime('%H:%M')})."
        }, status=400, json_dumps_params={'ensure_ascii': False})

    conflitos = buscar_reservas_conflitantes(
        veiculo=veiculo,
        data_reserva=data_val,
        horario_saida=saida_val,
        horario_retorno=retorno_val,
        reserva_id_ignorar=int(reserva_id) if reserva_id and str(reserva_id).isdigit() else None
    )

    tem_conflito = len(conflitos) > 0
    detalhes_conflitos = [
        {
            "id": c.id,
            "solicitante": c.solicitante,
            "atividade": c.atividade,
            "horario_saida": c.horario_saida.strftime('%H:%M'),
            "horario_retorno": c.horario_retorno.strftime('%H:%M'),
        }
        for c in conflitos
    ]

    return JsonResponse({
        "sucesso": True,
        "conflito_detectado": tem_conflito,
        "mensagem": (
            f"Conflito detectado: o veículo {veiculo.codigo} já possui reserva ativa neste intervalo."
            if tem_conflito else
            f"Veículo {veiculo.codigo} está disponível para o horário solicitado."
        ),
        "consulta": {
            "veiculo": veiculo.codigo,
            "data": data_val.strftime('%Y-%m-%d'),
            "horario_saida": saida_val.strftime('%H:%M'),
            "horario_retorno": retorno_val.strftime('%H:%M'),
        },
        "reservas_em_conflito": detalhes_conflitos
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})
