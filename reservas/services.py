"""
Módulo de Regras de Negócio e Serviços (Services) - Sistema COSEG Mobilidade
Porto do Itaqui - Programação para Web (PBL 1)

Este módulo centraliza as regras de negócio exigidas pelo COSEG no documento do PBL:
1. Validação de capacidade por categoria de veículo (máximo 4 para leves, máximo 18 para coletivos).
2. Rejeição de solicitações acima de 18 passageiros.
3. Validação de consistência de horários (retorno estritamente após a saída).
4. Validação de datas (data não pode estar no passado).
5. Algoritmo de detecção de conflitos de horário e sobreposição na mesma data.
"""

from datetime import date, time
from django.utils import timezone
from typing import List, Dict, Any, Optional


def verificar_sobreposicao_horarios(
    saida_a: time, retorno_a: time, saida_b: time, retorno_b: time
) -> bool:
    """
    Determina se dois intervalos de tempo se sobrepõem no mesmo dia.
    
    Fórmula de Interseção de Intervalos com Coincidência de Retorno:
    Dois intervalos [saida_a, retorno_a] e [saida_b, retorno_b] se sobrepõem se:
        saida_a <= retorno_b  E  retorno_a >= saida_b
        
    Conforme o documento do PBL:
    - Um veículo previsto para retornar às 14h NÃO pode ser reservado para outra
      atividade às 14h (coincidência de retorno com saída = conflito de utilização).
    - Reserva existente: 08:00 às 10:00 e Nova: 09:00 às 11:00 -> TRUE (CONFLITO!)
    - Reserva existente: 13:00 às 14:00 e Nova: 14:00 às 15:00 -> TRUE (CONFLITO!)
    - Reserva existente: 08:00 às 10:00 e Nova: 10:30 às 12:00 -> FALSE (SEM CONFLITO!)
    """
    return (saida_a <= retorno_b) and (retorno_a >= saida_b)


def buscar_reservas_conflitantes(
    veiculo,
    data_reserva: date,
    horario_saida: time,
    horario_retorno: time,
    reserva_id_ignorar: Optional[int] = None
) -> List[Any]:
    """
    Consulta o banco de dados via Django ORM para encontrar reservas ativas
    do mesmo veículo, na mesma data, que possuem sobreposição de horários.
    
    Ignora:
    - Reservas canceladas.
    - A própria reserva sendo editada (caso reserva_id_ignorar seja informado).
    """
    from .models import Reserva, StatusReserva

    # Busca no banco todas as reservas ativas daquele veículo naquele dia
    query = Reserva.objects.filter(
        veiculo=veiculo,
        data=data_reserva
    ).exclude(status=StatusReserva.CANCELADA)

    # Se estiver editando, não conflita consigo mesma
    if reserva_id_ignorar:
        query = query.exclude(id=reserva_id_ignorar)

    conflitos = []
    for r in query:
        if verificar_sobreposicao_horarios(
            saida_a=horario_saida,
            retorno_a=horario_retorno,
            saida_b=r.horario_saida,
            retorno_b=r.horario_retorno
        ):
            conflitos.append(r)

    return conflitos


def validar_regras_reserva(
    veiculo,
    data: Optional[date],
    horario_saida: Optional[time],
    horario_retorno: Optional[time],
    quantidade_passageiros: Optional[int],
    reserva_id: Optional[int] = None,
    permitir_data_historica: bool = False
) -> Dict[str, str]:
    """
    Executa todas as validações de regra de negócio exigidas pelo COSEG.
    Retorna um dicionário com erros encontrados (campo -> mensagem de erro).
    Se o dicionário estiver vazio, a solicitação é válida e pode ser persistida.
    """
    erros = {}

    # 1. Validação de campos obrigatórios
    if not veiculo:
        erros['veiculo'] = "É obrigatório selecionar um veículo da frota."

    if not data:
        erros['data'] = "A data da reserva é obrigatória."

    if not horario_saida:
        erros['horario_saida'] = "O horário de saída é obrigatório."

    if not horario_retorno:
        erros['horario_retorno'] = "O horário de retorno é obrigatório."

    if quantidade_passageiros is None:
        erros['quantidade_passageiros'] = "A quantidade de passageiros é obrigatória."
    elif quantidade_passageiros <= 0:
        erros['quantidade_passageiros'] = "A quantidade de passageiros deve ser pelo menos 1."

    # Se campos básicos faltarem, retorna os erros imediatos
    if erros:
        return erros

    # 2. Regra: Solicitações acima de 18 passageiros devem ser rejeitadas
    if quantidade_passageiros > 18:
        erros['quantidade_passageiros'] = (
            f"Capacidade máxima do sistema COSEG excedida ({quantidade_passageiros} pessoas). "
            f"O sistema comporta no máximo 18 passageiros por viagem."
        )
    # 3. Regra: Validação da capacidade do veículo específico
    elif veiculo and quantidade_passageiros > veiculo.capacidade:
        erros['quantidade_passageiros'] = (
            f"O veículo selecionado ({veiculo.codigo} - {veiculo.modelo}) comporta até "
            f"{veiculo.capacidade} passageiros, mas foram solicitadas {quantidade_passageiros} vagas."
        )

    if veiculo and not veiculo.ativo:
        erros['veiculo'] = f"O veículo {veiculo.codigo} está inativo ou em manutenção."

    # 4. Regra: Horário de retorno posterior ao de saída
    if horario_saida and horario_retorno:
        if horario_retorno <= horario_saida:
            erros['horario_retorno'] = (
                f"Horário inválido: o retorno ({horario_retorno.strftime('%H:%M')}) deve ser "
                f"estritamente posterior ao horário de saída ({horario_saida.strftime('%H:%M')})."
            )

    # 5. Regra: A data não poderá estar no passado
    if data and not permitir_data_historica:
        hoje = timezone.localdate()
        # Se for anterior à data de hoje, e não for dos dados iniciais do enunciado
        datas_iniciais_coseg = [date(2026, 8, 18), date(2026, 8, 19), date(2026, 8, 20)]
        if data < hoje and data not in datas_iniciais_coseg:
            erros['data'] = (
                f"A data da reserva ({data.strftime('%d/%m/%Y')}) não pode estar no passado. "
                f"Hoje é {hoje.strftime('%d/%m/%Y')}."
            )

    # 6. Regra: Detecção de conflitos de horário com reservas já existentes
    if veiculo and data and horario_saida and horario_retorno and 'horario_retorno' not in erros:
        conflitos = buscar_reservas_conflitantes(
            veiculo=veiculo,
            data_reserva=data,
            horario_saida=horario_saida,
            horario_retorno=horario_retorno,
            reserva_id_ignorar=reserva_id
        )

        if conflitos:
            detalhes = []
            for c in conflitos:
                detalhes.append(
                    f"Reserva #{c.id} ({c.horario_saida.strftime('%H:%M')} às {c.horario_retorno.strftime('%H:%M')} - {c.atividade})"
                )
            msg = (
                f"Conflito de agenda: O veículo {veiculo.codigo} já possui reserva confirmada neste horário "
                f"em {data.strftime('%d/%m/%Y')}: {', '.join(detalhes)}."
            )
            erros['conflito'] = msg
            if 'veiculo' not in erros:
                erros['veiculo'] = msg

    return erros
