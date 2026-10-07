# 04 - Guia das Rotas e Endpoints da API JSON (Para Integração no PBL 2)

O servidor do **COSEG Mobilidade** foi arquitetado seguindo os princípios de uma API RESTful. Todas as respostas trafegam em formato `JSON` com cabeçalhos HTTP adequados (`Content-Type: application/json; charset=utf-8`).

Esta documentação serve como referência completa para a apresentação técnica do PBL 1 e para a integração com a interface Web que será desenvolvida no **PBL 2**.

---

## 📌 Sumário dos Endpoints

| Método | Rota | Descrição |
| :---: | :--- | :--- |
| `GET` | `/` | Informações do servidor e catálogo de endpoints |
| `GET` | `/veiculos/` | Lista todos os veículos da frota do COSEG |
| `POST` | `/veiculos/` | Cadastra um novo veículo na frota |
| `GET` | `/veiculos/<codigo>/` | Detalhes de um veículo e suas reservas agendadas |
| `GET` | `/reservas/` | Lista todas as reservas (com filtros por query param) |
| `POST` | `/reservas/` | Cria uma nova reserva aplicando as validações |
| `GET` | `/reservas/<id>/` | Consulta os detalhes de uma reserva específica |
| `PUT` | `/reservas/<id>/` | Atualiza uma reserva existente (revalidando conflitos) |
| `DELETE` | `/reservas/<id>/` | Cancela ou exclui uma reserva do banco |
| `POST` | `/reservas/verificar-conflito/` | Simula e detecta conflitos em tempo real |

---

## 🔍 Exemplos Práticos de Requisição e Resposta

### 1. `GET /veiculos/`
Retorna a frota de veículos disponíveis.
* **Exemplo de Resposta (200 OK):**
```json
{
  "sucesso": true,
  "total": 10,
  "veiculos": [
    {
      "id": 1,
      "codigo": "VL-01",
      "modelo": "Fiat Cronos 1.3",
      "placa": "ROO-1001",
      "categoria": "LEVE",
      "categoria_descricao": "Veículo Leve (Até 4 passageiros)",
      "capacidade_passageiros": 4,
      "ativo": true
    },
    {
      "id": 9,
      "codigo": "VC-01",
      "modelo": "Mercedes-Benz Sprinter Van",
      "placa": "COL-2001",
      "categoria": "COLETIVO",
      "categoria_descricao": "Veículo Coletivo (Até 18 passageiros)",
      "capacidade_passageiros": 18,
      "ativo": true
    }
  ]
}
```

---

### 2. `POST /reservas/` (Criar Reserva - Sucesso)
Registra uma nova reserva consistente.
* **Corpo da Requisição (JSON):**
```json
{
  "solicitante": "Lucas Silva - Coordenação de Operações",
  "setor": "Operações Portuárias",
  "atividade": "Inspeção de Atracação",
  "origem": "Porto do Itaqui - Prédio Administrativo",
  "destino": "Berço 104 - Cais Sul",
  "data": "2026-10-15",
  "horario_saida": "09:00",
  "horario_retorno": "11:30",
  "quantidade_passageiros": 3,
  "veiculo": "VL-01",
  "observacoes": "Necessário capacete e colete para os passageiros."
}
```
* **Resposta (201 Created):**
```json
{
  "sucesso": true,
  "mensagem": "Reserva #5 confirmada com sucesso para o veículo VL-01!",
  "dados": {
    "id": 5,
    "solicitante": "Lucas Silva - Coordenação de Operações",
    "veiculo": "VL-01",
    "data": "2026-10-15",
    "horario_saida": "09:00",
    "horario_retorno": "11:30",
    "passageiros": 3,
    "status": "CONFIRMADA"
  }
}
```

---

### 3. `POST /reservas/` (Rejeição por Conflito de Horário)
Quando uma solicitação sobrepõe uma reserva já confirmada.
* **Corpo da Requisição (JSON):**
```json
{
  "solicitante": "Renata Lima",
  "setor": "Manutenção",
  "atividade": "Visita Técnica",
  "origem": "Porto do Itaqui",
  "destino": "Centro",
  "data": "2026-10-15",
  "horario_saida": "10:00",
  "horario_retorno": "12:00",
  "quantidade_passageiros": 2,
  "veiculo": "VL-01"
}
```
* **Resposta (400 Bad Request):**
```json
{
  "sucesso": false,
  "mensagem": "A solicitação viola uma ou mais regras de negócio do COSEG.",
  "erros": {
    "conflito": "Conflito de agenda: O veículo VL-01 já possui reserva confirmada neste horário em 15/10/2026: Reserva #5 (09:00 às 11:30 - Inspeção de Atracação)."
  }
}
```

---

### 4. `POST /reservas/` (Rejeição por Excesso de Capacidade)
Tentativa de solicitar 7 passageiros em um veículo leve de 4 lugares (caso verídico da narrativa do PBL).
* **Resposta (400 Bad Request):**
```json
{
  "sucesso": false,
  "mensagem": "A solicitação viola uma ou mais regras de negócio do COSEG.",
  "erros": {
    "quantidade_passageiros": "O veículo selecionado (VL-01 - Fiat Cronos 1.3) comporta até 4 passageiros, mas foram solicitadas 7 vagas."
  }
}
```

---

### 5. `POST /reservas/verificar-conflito/` (Simulador de Conflito)
Endpoint criado para verificação preventiva antes mesmo do colaborador submeter a reserva.
* **Corpo da Requisição (JSON):**
```json
{
  "veiculo": "VL-01",
  "data": "2026-10-15",
  "horario_saida": "10:00",
  "horario_retorno": "12:00"
}
```
* **Resposta (200 OK):**
```json
{
  "sucesso": true,
  "conflito_detectado": true,
  "mensagem": "Conflito detectado: o veículo VL-01 já possui reserva ativa neste intervalo.",
  "reservas_em_conflito": [
    {
      "id": 5,
      "solicitante": "Lucas Silva - Coordenação de Operações",
      "atividade": "Inspeção de Atracação",
      "horario_saida": "09:00",
      "horario_retorno": "11:30"
    }
  ]
}
```
