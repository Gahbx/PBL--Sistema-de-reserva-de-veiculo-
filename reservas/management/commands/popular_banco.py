"""
Comando de Gerenciamento Django: popular_banco
Execução: python manage.py popular_banco

Cadastra automaticamente no banco de dados SQLite:
1. A frota oficial de 10 veículos do COSEG (8 leves e 2 coletivos).
2. Os dados de teste iniciais fornecidos no enunciado do PBL 1.
"""

from django.core.management.base import BaseCommand
from reservas.models import Veiculo, Reserva, CategoriaVeiculo, StatusReserva
import datetime


class Command(BaseCommand):
    help = "Popula o banco de dados com a frota oficial do COSEG e os dados de teste do PBL 1"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("===> Inicializando cadastro da frota oficial do COSEG..."))

        # Definição dos 10 veículos conforme especificação do PBL:
        # 8 veículos leves (capacidade 4) e 2 veículos coletivos (capacidade 18)
        frota_dados = [
            # Veículos Leves (4 passageiros)
            {"codigo": "VL-01", "modelo": "Fiat Cronos 1.3", "placa": "ROO-1001", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            {"codigo": "VL-02", "modelo": "Chevrolet Onix Plus", "placa": "ROO-1002", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            {"codigo": "VL-03", "modelo": "Toyota Yaris Sedan", "placa": "ROO-1003", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            {"codigo": "VL-04", "modelo": "Volkswagen Virtus", "placa": "ROO-1004", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            {"codigo": "VL-05", "modelo": "Hyundai HB20S", "placa": "ROO-1005", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            {"codigo": "VL-06", "modelo": "Fiat Cronos 1.3", "placa": "ROO-1006", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            {"codigo": "VL-07", "modelo": "Renault Logan Zen", "placa": "ROO-1007", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            {"codigo": "VL-08", "modelo": "Nissan Versa Exclusive", "placa": "ROO-1008", "categoria": CategoriaVeiculo.LEVE, "capacidade": 4},
            # Veículos Coletivos (18 passageiros)
            {"codigo": "VC-01", "modelo": "Mercedes-Benz Sprinter Van", "placa": "COL-2001", "categoria": CategoriaVeiculo.COLETIVO, "capacidade": 18},
            {"codigo": "VC-02", "modelo": "Renault Master Minibus", "placa": "COL-2002", "categoria": CategoriaVeiculo.COLETIVO, "capacidade": 18},
        ]

        veiculos_criados = 0
        veiculos_map = {}
        for item in frota_dados:
            veiculo, criado = Veiculo.objects.get_or_update = Veiculo.objects.update_or_create(
                codigo=item["codigo"],
                defaults={
                    "modelo": item["modelo"],
                    "placa": item["placa"],
                    "categoria": item["categoria"],
                    "capacidade": item["capacidade"],
                    "ativo": True,
                }
            )
            veiculo_obj = veiculo if isinstance(veiculo, Veiculo) else veiculo[0]
            veiculos_map[item["codigo"]] = veiculo_obj
            if criado:
                veiculos_criados += 1

        self.stdout.write(self.style.SUCCESS(f"Frota cadastrada com sucesso ({len(frota_dados)} veículos no total)!"))

        # Reservas iniciais fornecidas pelo COSEG no documento do PBL:
        # 1. VL-01 em 18/08/2026, das 8h às 10h, para reunião administrativa
        # 2. VL-03 em 18/08/2026, das 13h às 15h, para inspeção técnica
        # 3. VC-01 em 19/08/2026, das 9h às 12h, para treinamento
        # 4. VL-05 em 20/08/2026, das 14h às 17h, para visita externa
        reservas_iniciais = [
            {
                "veiculo_codigo": "VL-01",
                "solicitante": "Carlos Mendes - Coord. Financeira",
                "setor": "Administrativo / Financeiro",
                "atividade": "Reunião administrativa",
                "origem": "Porto do Itaqui - Prédio Central",
                "destino": "Secretaria da Fazenda (SEFAZ) - São Luís",
                "data": datetime.date(2026, 8, 18),
                "horario_saida": datetime.time(8, 0),
                "horario_retorno": datetime.time(10, 0),
                "quantidade_passageiros": 3,
                "observacoes": "Reunião orçamentária com a diretoria do Porto.",
            },
            {
                "veiculo_codigo": "VL-03",
                "solicitante": "Juliana Rocha - Engenheira Portuária",
                "setor": "Operações / Engenharia",
                "atividade": "Inspeção técnica",
                "origem": "Porto do Itaqui - Berço 102",
                "destino": "Terminal Graneleiro de Ponta da Madeira",
                "data": datetime.date(2026, 8, 18),
                "horario_saida": datetime.time(13, 0),
                "horario_retorno": datetime.time(15, 0),
                "quantidade_passageiros": 2,
                "observacoes": "Inspeção estrutural preventiva e verificação de defensas.",
            },
            {
                "veiculo_codigo": "VC-01",
                "solicitante": "Marcos Silveira - RH & Segurança",
                "setor": "Recursos Humanos / COSEG",
                "atividade": "Treinamento",
                "origem": "Porto do Itaqui - Centro de Treinamento",
                "destino": "Auditório do SENAI / Distrito Industrial",
                "data": datetime.date(2026, 8, 19),
                "horario_saida": datetime.time(9, 0),
                "horario_retorno": datetime.time(12, 0),
                "quantidade_passageiros": 16,
                "observacoes": "Treinamento de prevenção a acidentes e NR-29 (Trabalho Portuário).",
            },
            {
                "veiculo_codigo": "VL-05",
                "solicitante": "Beatriz Alencar - Relações Institucionais",
                "setor": "Comunicação & Parcerias",
                "atividade": "Visita externa",
                "origem": "Porto do Itaqui - Recepção",
                "destino": "Associação Comercial do Maranhão - Centro Histórico",
                "data": datetime.date(2026, 8, 20),
                "horario_saida": datetime.time(14, 0),
                "horario_retorno": datetime.time(17, 0),
                "quantidade_passageiros": 4,
                "observacoes": "Acompanhamento de comitiva internacional de logística marítima.",
            },
        ]

        reservas_criadas = 0
        for r_data in reservas_iniciais:
            veiculo = veiculos_map.get(r_data["veiculo_codigo"])
            if not veiculo:
                continue

            # Usar filter para não duplicar se já existir
            existe = Reserva.objects.filter(
                veiculo=veiculo,
                data=r_data["data"],
                horario_saida=r_data["horario_saida"],
                horario_retorno=r_data["horario_retorno"]
            ).first()

            if not existe:
                reserva = Reserva(
                    veiculo=veiculo,
                    solicitante=r_data["solicitante"],
                    setor=r_data["setor"],
                    atividade=r_data["atividade"],
                    origem=r_data["origem"],
                    destino=r_data["destino"],
                    data=r_data["data"],
                    horario_saida=r_data["horario_saida"],
                    horario_retorno=r_data["horario_retorno"],
                    quantidade_passageiros=r_data["quantidade_passageiros"],
                    observacoes=r_data["observacoes"],
                    status=StatusReserva.CONFIRMADA
                )
                # Salva usando super().save() para os dados históricos pré-carregados
                super(Reserva, reserva).save()
                reservas_criadas += 1

        self.stdout.write(self.style.SUCCESS(f"Reservas de teste do COSEG cadastradas com sucesso ({reservas_criadas} novas)!"))
        self.stdout.write(self.style.SUCCESS("Banco de dados pronto para testes e simulações do PBL 1!"))
