"""
Módulo de Modelos de Dados (Models) - Sistema COSEG Mobilidade
Porto do Itaqui - Programação para Web (PBL 1)

Este arquivo define a estrutura das tabelas do banco de dados (SQLite),
utilizando o Django ORM (Object-Relational Mapping).
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime


class CategoriaVeiculo(models.TextChoices):
    """
    Categorias de veículos disponíveis na frota do Porto do Itaqui:
    - LEVE: capacidade para até 4 passageiros (VL-01 a VL-08)
    - COLETIVO: capacidade para até 18 passageiros (VC-01 e VC-02)
    """
    LEVE = 'LEVE', 'Veículo Leve (Até 4 passageiros)'
    COLETIVO = 'COLETIVO', 'Veículo Coletivo (Até 18 passageiros)'


class Veiculo(models.Model):
    """
    Representa um veículo da frota oficial do COSEG.
    A frota total do problema é de 10 veículos:
    - 8 veículos leves (capacidade 4)
    - 2 veículos coletivos (capacidade 18)
    """
    codigo = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Código do Veículo",
        help_text="Exemplo: VL-01, VL-02, VC-01"
    )
    modelo = models.CharField(
        max_length=60,
        verbose_name="Modelo / Descrição",
        help_text="Exemplo: Fiat Cronos, Renault Master, etc."
    )
    placa = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Placa do Veículo",
        help_text="Exemplo: BRA2E19"
    )
    categoria = models.CharField(
        max_length=10,
        choices=CategoriaVeiculo.choices,
        default=CategoriaVeiculo.LEVE,
        verbose_name="Categoria"
    )
    capacidade = models.PositiveIntegerField(
        verbose_name="Capacidade de Passageiros",
        help_text="Número máximo de passageiros permitidos (4 ou 18)"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo na Frota",
        help_text="Define se o veículo está apto para receber novas reservas"
    )

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.modelo} ({self.get_categoria_display()} - {self.capacidade} lug.)"

    def clean(self):
        super().clean()
        if self.categoria == CategoriaVeiculo.LEVE and self.capacidade and self.capacidade > 4:
            raise ValidationError({'capacidade': "Veículos da categoria LEVE comportam no máximo 4 passageiros."})
        elif self.categoria == CategoriaVeiculo.COLETIVO and self.capacidade and self.capacidade > 18:
            raise ValidationError({'capacidade': "Veículos da categoria COLETIVO comportam no máximo 18 passageiros."})


class StatusReserva(models.TextChoices):
    """
    Status possíveis para o ciclo de vida de uma reserva.
    """
    CONFIRMADA = 'CONFIRMADA', 'Confirmada'
    CONCLUIDA = 'CONCLUIDA', 'Concluída'
    CANCELADA = 'CANCELADA', 'Cancelada'


class Reserva(models.Model):
    """
    Representa a solicitação e registro persistente de reserva de veículo do COSEG.
    Armazena todos os dados definidos no documento do PBL e aplica as validações
    essenciais de negócio antes de persistir no banco de dados.
    """
    solicitante = models.CharField(
        max_length=100,
        verbose_name="Identificação do Solicitante",
        help_text="Nome completo ou matrícula do colaborador"
    )
    setor = models.CharField(
        max_length=80,
        verbose_name="Setor do Porto",
        help_text="Setor solicitante (ex: Operações, Manutenção, Administrativo, TI)"
    )
    atividade = models.CharField(
        max_length=120,
        verbose_name="Finalidade / Atividade",
        help_text="Exemplo: Reunião administrativa, Inspeção técnica, Treinamento, Visita externa"
    )
    origem = models.CharField(
        max_length=120,
        verbose_name="Local de Origem",
        help_text="Ponto de partida do deslocamento"
    )
    destino = models.CharField(
        max_length=120,
        verbose_name="Local de Destino",
        help_text="Destino final da atividade"
    )
    data = models.DateField(
        verbose_name="Data da Reserva",
        help_text="Data do deslocamento (não pode ser anterior à data de hoje)"
    )
    horario_saida = models.TimeField(
        verbose_name="Horário de Saída",
        help_text="Horário previsto para o início da viagem"
    )
    horario_retorno = models.TimeField(
        verbose_name="Horário de Retorno",
        help_text="Horário previsto para o término da viagem (deve ser posterior à saída)"
    )
    quantidade_passageiros = models.PositiveIntegerField(
        verbose_name="Quantidade de Passageiros",
        help_text="Total de pessoas que serão transportadas (máximo 18 no sistema)"
    )
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name="Veículo Solicitado"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Informações adicionais relevantes para o motorista ou COSEG"
    )
    status = models.CharField(
        max_length=15,
        choices=StatusReserva.choices,
        default=StatusReserva.CONFIRMADA,
        verbose_name="Status da Reserva"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora de Registro"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Reserva de Veículo"
        verbose_name_plural = "Reservas de Veículos"
        ordering = ['-data', 'horario_saida']

    def __str__(self):
        try:
            codigo = self.veiculo.codigo if self.veiculo else "Sem veículo"
        except Exception:
            codigo = "Sem veículo"
        data_str = self.data.strftime('%d/%m/%Y') if self.data else "Data pendente"
        saida_str = self.horario_saida.strftime('%H:%M') if self.horario_saida else "--:--"
        retorno_str = self.horario_retorno.strftime('%H:%M') if self.horario_retorno else "--:--"
        solicitante_str = self.solicitante or "Pendente"
        return f"Reserva #{self.id or 'Nova'} - {codigo} em {data_str} ({saida_str} às {retorno_str}) - {solicitante_str}"

    def clean(self):
        """
        Executa as validações de regra de negócio do servidor antes de salvar:
        1. Quantidade de passageiros acima do limite global do sistema (máx 18).
        2. Quantidade de passageiros excedendo a capacidade do veículo selecionado.
        3. Data no passado.
        4. Horário de retorno menor ou igual ao horário de saída.
        5. Conflito / sobreposição de horários com reservas ativas existentes para o mesmo veículo na mesma data.
        """
        from .services import validar_regras_reserva
        try:
            veiculo = self.veiculo
        except Exception:
            veiculo = None

        erros = validar_regras_reserva(
            veiculo=veiculo,
            data=getattr(self, 'data', None),
            horario_saida=getattr(self, 'horario_saida', None),
            horario_retorno=getattr(self, 'horario_retorno', None),
            quantidade_passageiros=getattr(self, 'quantidade_passageiros', None),
            reserva_id=self.id
        )
        if erros:
            # Mapeia os erros apenas para campos reais do model para o Django Admin
            # renderizar a caixa de erro amigável na interface sem estourar ValueError
            campos_validos = {f.name for f in self._meta.fields}
            erros_model = {}
            for campo, msg in erros.items():
                if campo in campos_validos:
                    erros_model[campo] = msg
                elif campo == 'conflito':
                    erros_model['veiculo'] = msg
                else:
                    erros_model['__all__'] = msg
            raise ValidationError(erros_model)

    def save(self, *args, **kwargs):
        """
        Garante que clean() seja sempre invocado antes de salvar,
        mesmo quando criado diretamente via ORM Reserva.objects.create().
        """
        self.full_clean()
        super().save(*args, **kwargs)
