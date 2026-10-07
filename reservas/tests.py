"""
Bateria de Testes Automatizados - Camada de Servidor do COSEG Mobilidade
Porto do Itaqui - Programação para Web (PBL 1)

Este módulo testa e fornece evidências de todas as exigências do PBL:
1. Persistência de dados no banco e operações CRUD
2. Validação da capacidade da frota (leves até 4, coletivos até 18, rejeição > 18)
3. Validação de horários (retorno posterior à saída)
4. Validação de data não permitida no passado
5. Detecção matemática de conflitos e sobreposição de horários
6. Cenários reais fornecidos pela banca/professor no documento do PBL
"""

import json
from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.core.exceptions import ValidationError

from reservas.models import Veiculo, Reserva, CategoriaVeiculo, StatusReserva
from reservas.services import (
    verificar_sobreposicao_horarios,
    buscar_reservas_conflitantes,
    validar_regras_reserva,
)


class TestFrotaVeiculos(TestCase):
    """
    Testa o cadastro e persistência da frota oficial do COSEG.
    """
    def setUp(self):
        self.vl01 = Veiculo.objects.create(
            codigo="VL-01",
            modelo="Fiat Cronos 1.3",
            categoria=CategoriaVeiculo.LEVE,
            capacidade=4
        )
        self.vc01 = Veiculo.objects.create(
            codigo="VC-01",
            modelo="Mercedes-Benz Sprinter",
            categoria=CategoriaVeiculo.COLETIVO,
            capacidade=18
        )

    def test_persistencia_veiculo(self):
        """Verifica se o veículo foi gravado com sucesso no SQLite."""
        veiculo_banco = Veiculo.objects.get(codigo="VL-01")
        self.assertEqual(veiculo_banco.modelo, "Fiat Cronos 1.3")
        self.assertEqual(veiculo_banco.capacidade, 4)
        self.assertEqual(veiculo_banco.categoria, CategoriaVeiculo.LEVE)

    def test_veiculo_coletivo_capacidade(self):
        """Verifica capacidade de veículo coletivo."""
        veiculo_coletivo = Veiculo.objects.get(codigo="VC-01")
        self.assertEqual(veiculo_coletivo.capacidade, 18)


class TestRegrasDeNegocioValidacoes(TestCase):
    """
    Testa o cumprimento estrito das regras de negócio do PBL.
    """
    def setUp(self):
        self.veiculo_leve = Veiculo.objects.create(
            codigo="VL-01",
            modelo="Fiat Cronos",
            categoria=CategoriaVeiculo.LEVE,
            capacidade=4
        )
        self.veiculo_coletivo = Veiculo.objects.create(
            codigo="VC-01",
            modelo="Mercedes Sprinter",
            categoria=CategoriaVeiculo.COLETIVO,
            capacidade=18
        )
        self.amanha = timezone.localdate() + timedelta(days=2)

    def test_rejeicao_acima_de_18_passageiros(self):
        """Regra do PBL: Solicitações acima de 18 passageiros devem ser rejeitadas."""
        erros = validar_regras_reserva(
            veiculo=self.veiculo_coletivo,
            data=self.amanha,
            horario_saida=time(8, 0),
            horario_retorno=time(12, 0),
            quantidade_passageiros=19  # Excede o teto máximo de 18
        )
        self.assertIn('quantidade_passageiros', erros)
        self.assertIn("Capacidade máxima do sistema COSEG excedida", erros['quantidade_passageiros'])

    def test_rejeicao_capacidade_excedida_veiculo_leve(self):
        """
        Regra do PBL: Em um veículo com 4 lugares solicitado para 7 pessoas
        (caso real relatado na narrativa), o sistema deve rejeitar.
        """
        erros = validar_regras_reserva(
            veiculo=self.veiculo_leve,
            data=self.amanha,
            horario_saida=time(9, 0),
            horario_retorno=time(11, 0),
            quantidade_passageiros=7  # VL comporta 4
        )
        self.assertIn('quantidade_passageiros', erros)
        self.assertIn("comporta até 4 passageiros", erros['quantidade_passageiros'])

    def test_rejeicao_horario_retorno_invalido(self):
        """
        Regra do PBL: O horário de retorno deverá ser estritamente posterior
        ao horário de saída.
        """
        # Horário de retorno igual ao de saída
        erros_igual = validar_regras_reserva(
            veiculo=self.veiculo_leve,
            data=self.amanha,
            horario_saida=time(14, 0),
            horario_retorno=time(14, 0),
            quantidade_passageiros=3
        )
        self.assertIn('horario_retorno', erros_igual)

        # Horário de retorno anterior ao de saída
        erros_anterior = validar_regras_reserva(
            veiculo=self.veiculo_leve,
            data=self.amanha,
            horario_saida=time(14, 0),
            horario_retorno=time(11, 0),
            quantidade_passageiros=3
        )
        self.assertIn('horario_retorno', erros_anterior)

    def test_rejeicao_data_no_passado(self):
        """Regra do PBL: A data não poderá estar no passado."""
        ontem = timezone.localdate() - timedelta(days=1)
        erros = validar_regras_reserva(
            veiculo=self.veiculo_leve,
            data=ontem,
            horario_saida=time(8, 0),
            horario_retorno=time(10, 0),
            quantidade_passageiros=2
        )
        self.assertIn('data', erros)
        self.assertIn("não pode estar no passado", erros['data'])


class TestDetecaoConflitoHorarios(TestCase):
    """
    Testa o algoritmo de identificação de conflitos e sobreposição de horários
    conforme apresentado na Aula 07 e no documento do PBL.
    """
    def setUp(self):
        self.veiculo = Veiculo.objects.create(
            codigo="VL-01",
            modelo="Fiat Cronos",
            categoria=CategoriaVeiculo.LEVE,
            capacidade=4
        )
        self.data_teste = timezone.localdate() + timedelta(days=5)

        # Cadastra reserva base: 08:00 às 10:00
        self.reserva_base = Reserva.objects.create(
            solicitante="Danilo Costa",
            setor="Tecnologia",
            atividade="Reunião de Alinhamento",
            origem="Porto do Itaqui",
            destino="Centro",
            data=self.data_teste,
            horario_saida=time(8, 0),
            horario_retorno=time(10, 0),
            quantidade_passageiros=3,
            veiculo=self.veiculo
        )

    def test_formula_matematica_sobreposicao(self):
        """Valida a função pura de sobreposição de intervalos temporais."""
        # Reserva base: 08h às 10h

        # Sobreposição: 09h às 11h (começa antes da base terminar)
        self.assertTrue(verificar_sobreposicao_horarios(time(9, 0), time(11, 0), time(8, 0), time(10, 0)))

        # Sobreposição: 08h30 às 09h30 (dentro da base)
        self.assertTrue(verificar_sobreposicao_horarios(time(8, 30), time(9, 30), time(8, 0), time(10, 0)))

        # Sem sobreposição: 10h30 às 12h (começa após o término)
        self.assertFalse(verificar_sobreposicao_horarios(time(10, 30), time(12, 0), time(8, 0), time(10, 0)))

        # Sem sobreposição: 10h00 às 12h00 (saída coincide com o retorno da anterior)
        self.assertFalse(verificar_sobreposicao_horarios(time(10, 0), time(12, 0), time(8, 0), time(10, 0)))

        # Sem sobreposição: 06h00 às 08h00 (retorno coincide com a saída da seguinte)
        self.assertFalse(verificar_sobreposicao_horarios(time(6, 0), time(8, 0), time(8, 0), time(10, 0)))

    def test_cenario_conflito_do_documento_pbl(self):
        """
        Cenário explícito do documento do PBL:
        'Por exemplo, uma reserva existente das 8h às 10h entra em conflito com uma nova reserva das 9h às 11h'
        """
        erros = validar_regras_reserva(
            veiculo=self.veiculo,
            data=self.data_teste,
            horario_saida=time(9, 0),
            horario_retorno=time(11, 0),
            quantidade_passageiros=2
        )
        self.assertIn('conflito', erros)

    def test_cenario_sem_conflito_do_documento_pbl(self):
        """
        Cenário explícito do documento do PBL:
        'uma nova reserva das 10h30 às 12h não apresenta sobreposição.'
        """
        erros = validar_regras_reserva(
            veiculo=self.veiculo,
            data=self.data_teste,
            horario_saida=time(10, 30),
            horario_retorno=time(12, 0),
            quantidade_passageiros=2
        )
        self.assertEqual(len(erros), 0)


class TestCenariosOficiaisCOSEG(TestCase):
    """
    Testa o conjunto exato de reservas de teste fornecido pelo COSEG na página 3:
    1. VL-01 em 18/08/2026, 8h às 10h (reunião administrativa)
    2. VL-03 em 18/08/2026, 13h às 15h (inspeção técnica)
    3. VC-01 em 19/08/2026, 9h às 12h (treinamento)
    4. VL-05 em 20/08/2026, 14h às 17h (visita externa)
    """
    def setUp(self):
        self.vl01 = Veiculo.objects.create(codigo="VL-01", modelo="Fiat Cronos", categoria=CategoriaVeiculo.LEVE, capacidade=4)
        self.vl03 = Veiculo.objects.create(codigo="VL-03", modelo="Toyota Yaris", categoria=CategoriaVeiculo.LEVE, capacidade=4)
        self.vc01 = Veiculo.objects.create(codigo="VC-01", modelo="Mercedes Sprinter", categoria=CategoriaVeiculo.COLETIVO, capacidade=18)
        self.vl05 = Veiculo.objects.create(codigo="VL-05", modelo="Hyundai HB20S", categoria=CategoriaVeiculo.LEVE, capacidade=4)

        # Cadastro das reservas iniciais do COSEG
        super(Reserva, Reserva(
            veiculo=self.vl01, solicitante="Carlos Mendes", setor="Administrativo",
            atividade="Reunião administrativa", origem="Porto", destino="SEFAZ",
            data=date(2026, 8, 18), horario_saida=time(8, 0), horario_retorno=time(10, 0),
            quantidade_passageiros=3
        )).save()

        super(Reserva, Reserva(
            veiculo=self.vl03, solicitante="Juliana Rocha", setor="Operações",
            atividade="Inspeção técnica", origem="Porto", destino="Ponta da Madeira",
            data=date(2026, 8, 18), horario_saida=time(13, 0), horario_retorno=time(15, 0),
            quantidade_passageiros=2
        )).save()

        super(Reserva, Reserva(
            veiculo=self.vc01, solicitante="Marcos Silveira", setor="RH",
            atividade="Treinamento", origem="Porto", destino="SENAI",
            data=date(2026, 8, 19), horario_saida=time(9, 0), horario_retorno=time(12, 0),
            quantidade_passageiros=16
        )).save()

        super(Reserva, Reserva(
            veiculo=self.vl05, solicitante="Beatriz Alencar", setor="Relações Inst.",
            atividade="Visita externa", origem="Porto", destino="Assoc. Comercial",
            data=date(2026, 8, 20), horario_saida=time(14, 0), horario_retorno=time(17, 0),
            quantidade_passageiros=4
        )).save()

    def test_todas_as_reservas_iniciais_persistidas(self):
        """Verifica se as 4 reservas iniciais do COSEG estão gravadas no banco."""
        self.assertEqual(Reserva.objects.count(), 4)

    def test_conflito_com_reserva_do_enunciado(self):
        """
        Tentativa de reservar o VL-01 no dia 18/08/2026 das 09h às 11h
        deve colidir com a reserva existente das 08h às 10h.
        """
        erros = validar_regras_reserva(
            veiculo=self.vl01,
            data=date(2026, 8, 18),
            horario_saida=time(9, 0),
            horario_retorno=time(11, 0),
            quantidade_passageiros=3,
            permitir_data_historica=True
        )
        self.assertIn('conflito', erros)

    def test_sucesso_sem_conflito_com_reserva_do_enunciado(self):
        """
        Reserva para o VL-01 no dia 18/08/2026 das 10h30 às 12h
        não tem sobreposição e deve ser aceita.
        """
        erros = validar_regras_reserva(
            veiculo=self.vl01,
            data=date(2026, 8, 18),
            horario_saida=time(10, 30),
            horario_retorno=time(12, 0),
            quantidade_passageiros=3,
            permitir_data_historica=True
        )
        self.assertEqual(len(erros), 0)


class TestEndpointsAPI(TestCase):
    """
    Testa as operações CRUD e endpoints HTTP via cliente de teste Django.
    Garante que as rotas da camada de servidor respondam em JSON com status correto.
    """
    def setUp(self):
        self.client = Client()
        self.veiculo = Veiculo.objects.create(
            codigo="VL-01",
            modelo="Fiat Cronos",
            categoria=CategoriaVeiculo.LEVE,
            capacidade=4
        )
        self.data_valida = timezone.localdate() + timedelta(days=3)

    def test_api_catalogo_index(self):
        """GET / -> Apresenta o servidor e endpoints disponíveis."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        dados = resp.json()
        self.assertEqual(dados['status'], "Online e operacional")
        self.assertIn('endpoints', dados)

    def test_api_listar_veiculos(self):
        """GET /veiculos/ -> Retorna frota cadastrada em JSON."""
        resp = self.client.get('/veiculos/')
        self.assertEqual(resp.status_code, 200)
        dados = resp.json()
        self.assertTrue(dados['sucesso'])
        self.assertEqual(dados['total'], 1)
        self.assertEqual(dados['veiculos'][0]['codigo'], "VL-01")

    def test_api_criar_reserva_sucesso_crud_create(self):
        """POST /reservas/ -> Cria reserva válida com status 201 Created."""
        payload = {
            "solicitante": "Eng. Roberto Dias",
            "setor": "Manutenção Portuária",
            "atividade": "Inspeção em Guindaste",
            "origem": "Prédio Administrativo",
            "destino": "Cais do Porto",
            "data": self.data_valida.strftime('%Y-%m-%d'),
            "horario_saida": "08:00",
            "horario_retorno": "10:00",
            "quantidade_passageiros": 3,
            "veiculo": self.veiculo.codigo
        }
        resp = self.client.post('/reservas/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        dados = resp.json()
        self.assertTrue(dados['sucesso'])
        self.assertIn('id', dados['dados'])
        self.assertGreater(dados['dados']['id'], 0)

    def test_api_criar_reserva_rejeitada_por_conflito(self):
        """POST /reservas/ -> Rejeita reserva conflitante com status 400 Bad Request."""
        # Cria primeira reserva das 08h às 10h
        Reserva.objects.create(
            solicitante="Primeiro Solicitante",
            setor="Operações",
            atividade="Reunião",
            origem="Origem",
            destino="Destino",
            data=self.data_valida,
            horario_saida=time(8, 0),
            horario_retorno=time(10, 0),
            quantidade_passageiros=2,
            veiculo=self.veiculo
        )

        # Tenta criar segunda reserva das 09h às 11h
        payload_conflito = {
            "solicitante": "Segundo Solicitante",
            "setor": "Logística",
            "atividade": "Deslocamento",
            "origem": "Origem",
            "destino": "Destino",
            "data": self.data_valida.strftime('%Y-%m-%d'),
            "horario_saida": "09:00",
            "horario_retorno": "11:00",
            "quantidade_passageiros": 2,
            "veiculo": self.veiculo.codigo
        }
        resp = self.client.post('/reservas/', data=json.dumps(payload_conflito), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        dados = resp.json()
        self.assertFalse(dados['sucesso'])
        self.assertIn('conflito', dados['erros'])

    def test_api_reserva_crud_read_update_delete(self):
        """Testa o ciclo de leitura, atualização e cancelamento de uma reserva."""
        # 1. Criação
        reserva = Reserva.objects.create(
            solicitante="Maria Silva",
            setor="TI",
            atividade="Suporte Técnico",
            origem="Sede",
            destino="Berço 100",
            data=self.data_valida,
            horario_saida=time(14, 0),
            horario_retorno=time(16, 0),
            quantidade_passageiros=2,
            veiculo=self.veiculo
        )

        # 2. READ (GET)
        resp_get = self.client.get(f'/reservas/{reserva.id}/')
        self.assertEqual(resp_get.status_code, 200)
        self.assertEqual(resp_get.json()['dados']['solicitante'], "Maria Silva")

        # 3. UPDATE (PUT)
        payload_update = {
            "atividade": "Suporte Avançado em Redes Fibra",
            "quantidade_passageiros": 3
        }
        resp_put = self.client.put(
            f'/reservas/{reserva.id}/',
            data=json.dumps(payload_update),
            content_type='application/json'
        )
        self.assertEqual(resp_put.status_code, 200)
        reserva.refresh_from_db()
        self.assertEqual(reserva.atividade, "Suporte Avançado em Redes Fibra")
        self.assertEqual(reserva.quantidade_passageiros, 3)

        # 4. DELETE (Cancelamento)
        resp_del = self.client.delete(f'/reservas/{reserva.id}/')
        self.assertEqual(resp_del.status_code, 200)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, StatusReserva.CANCELADA)

    def test_api_verificar_conflito_endpoint(self):
        """POST /reservas/verificar-conflito/ -> Consulta rápida sem persistir."""
        # Reserva base: 08:00 às 10:00
        Reserva.objects.create(
            solicitante="Teste",
            setor="Setor",
            atividade="Atividade",
            origem="Origem",
            destino="Destino",
            data=self.data_valida,
            horario_saida=time(8, 0),
            horario_retorno=time(10, 0),
            quantidade_passageiros=2,
            veiculo=self.veiculo
        )

        # Consulta horário conflitante (09:00 às 11:00)
        resp_conflito = self.client.post('/reservas/verificar-conflito/', data=json.dumps({
            "veiculo": self.veiculo.codigo,
            "data": self.data_valida.strftime('%Y-%m-%d'),
            "horario_saida": "09:00",
            "horario_retorno": "11:00"
        }), content_type='application/json')
        self.assertEqual(resp_conflito.status_code, 200)
        self.assertTrue(resp_conflito.json()['conflito_detectado'])

        # Consulta horário livre (11:00 às 13:00)
        resp_livre = self.client.post('/reservas/verificar-conflito/', data=json.dumps({
            "veiculo": self.veiculo.codigo,
            "data": self.data_valida.strftime('%Y-%m-%d'),
            "horario_saida": "11:00",
            "horario_retorno": "13:00"
        }), content_type='application/json')
        self.assertEqual(resp_livre.status_code, 200)
        self.assertFalse(resp_livre.json()['conflito_detectado'])
