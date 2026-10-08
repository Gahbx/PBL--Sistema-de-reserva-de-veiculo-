# 🚗 COSEG Mobilidade — Sistema de Reserva de Veículos

Sistema back-end em **Python / Django** para gerenciamento centralizado e persistente da frota corporativa do setor **COSEG (Porto do Itaqui)**. Desenvolvido para eliminar conflitos de horários, incompatibilidades de capacidade e pedidos descentralizados.

---

## 📌 1. Pontos Principais do Sistema

### 🚘 Frota Oficial (10 Veículos)
- **8 Veículos Leves (`VL-01` a `VL-08`):** Capacidade para até **4 passageiros**.
- **2 Veículos Coletivos (`VC-01` e `VC-02`):** Capacidade para até **18 passageiros**.

### 🛡️ Regras de Negócio Centrais
1. **Capacidade do Veículo:** Bloqueia qualquer solicitação acima de 18 passageiros ou que exceda a lotação do veículo escolhido (ex: 7 pessoas em veículo de 4 lugares).
2. **Consistência de Horários:** O horário de retorno deve ser estritamente posterior ao horário de saída.
3. **Bloqueio de Data no Passado:** Impede agendamentos em datas retroativas.
4. **Algoritmo Anticonflito (Sobreposição de Horários):** Impede reservas conflitantes para o mesmo veículo na mesma data através da regra:
   $$\text{Conflito} \iff (\text{saída}_{\text{nova}} < \text{retorno}_{\text{existente}}) \land (\text{retorno}_{\text{nova}} > \text{saída}_{\text{existente}})$$

### 🗄️ Modelagem Limpa no SQLite (`db.sqlite3`)
O banco contém exclusivamente as entidades do domínio da aplicação:
- **`Veiculo` (`reservas_veiculo`):** `codigo`, `modelo`, `placa`, `categoria`, `capacidade`, `ativo`.
- **`Reserva` (`reservas_reserva`):** `solicitante`, `setor`, `atividade`, `origem`, `destino`, `data`, `horario_saida`, `horario_retorno`, `quantidade_passageiros`, `veiculo` (chave estrangeira), `observacoes`, `status`, `criado_em`, `atualizado_em`.

### 📡 Rotas da API JSON
| Método | Endpoint | Descrição |
| :---: | :--- | :--- |
| `GET` | `/` | Apresentação do sistema e catálogo de rotas |
| `GET` | `/veiculos/` | Lista toda a frota e capacidades |
| `POST` | `/veiculos/` | Cadastra novo veículo |
| `GET` | `/veiculos/<codigo>/` | Detalhes de um veículo específico |
| `GET` | `/reservas/` | Lista reservas (filtros: `?data=`, `?veiculo=`, `?status=`) |
| `POST` | `/reservas/` | Registra nova reserva (aplica todas as validações) |
| `GET` | `/reservas/<id>/` | Detalhes de uma reserva específica |
| `PUT` | `/reservas/<id>/` | Atualiza reserva existente (revalida regras) |
| `DELETE` | `/reservas/<id>/` | Cancela (`status=CANCELADA`) uma reserva |
| `POST` | `/reservas/verificar-conflito/` | Simula disponibilidade de horário sem persistir |

---

## 🚀 2. Códigos para Iniciar o Sistema

Abra o terminal na pasta do projeto e execute:

```bash
# 1. Instalar as dependências
pip install -r requirements.txt

# 2. Criar as tabelas no banco SQLite
python manage.py migrate

# 3. Popular a frota oficial (10 veículos) e as 4 reservas de teste do COSEG
python manage.py popular_banco

# 4. Rodar a suíte de testes automatizados (18 testes)
python manage.py test

# 5. Iniciar o servidor local
python manage.py runserver
```

> **Acesso ao Servidor:**
> - 🛠️ **Interface Web Administrativa:** `http://127.0.0.1:8000/admin/`  
>   - **Usuário:** `admin` | **Senha:** `admin123`
> - 🌐 **API REST (JSON):** `http://127.0.0.1:8000/`

---

## 🧪 3. Guia Prático de Testes na Interface Web (`runserver`)

Com o servidor rodando (`python manage.py runserver`), abra seu navegador em:  
👉 **`http://127.0.0.1:8000/admin/`**  
*(Faça login com usuário: `admin` e senha: `admin123`)*

Abaixo estão os testes práticos passo a passo para demonstrar na interface todas as regras exigidas no documento do PBL:

---

### 🔹 Teste 1: Cadastrar um Novo Veículo na Frota
1. Na tela inicial do painel, clique em **`+ Adicionar`** ao lado de **Veículos**.
2. Preencha os dados do novo carro:
   - **Código do Veículo:** `VL-09`
   - **Modelo / Descrição:** `Honda City 1.5 Sedan`
   - **Placa do Veículo:** `ROO-1009`
   - **Categoria:** `Veículo Leve (Até 4 passageiros)`
   - **Capacidade de Passageiros:** `4`
   - **Ativo na Frota:** `Marcado (Sim)`
3. Clique em **SALVAR**.
> **Resultado na tela:** O veículo é cadastrado com sucesso e passa a figurar na listagem da frota oficial disponível para novos agendamentos.

---

### 🔹 Teste 2: Criar uma Nova Reserva / Manifestação de Uso (Sucesso)
1. No painel, clique em **`+ Adicionar`** ao lado de **Reservas de Veículos**.
2. Preencha a manifestação formal da viagem com todos os campos de controle:
   - **Identificação do Solicitante:** `Fernanda Costa - Engenharia`
   - **Setor do Porto:** `Operações / Manutenção`
   - **Finalidade / Atividade:** `Vistoria no Cais Sul`
   - **Local de Origem:** `Portaria Principal`
   - **Local de Destino:** `Berço 103`
   - **Data da Reserva:** Coloque uma data futura (ex: `15/10/2026`)
   - **Horário de Saída:** `08:30`
   - **Horário de Retorno:** `11:30`
   - **Quantidade de Passageiros:** `3`
   - **Veículo Solicitado:** Selecione `VL-04 - Volkswagen Virtus`
3. Clique em **SALVAR**.
> **Resultado na tela:** Uma tarja verde de sucesso confirma o agendamento, garantindo que o carro foi reservado para o trajeto e horários definidos.

---

### 🔹 Teste 3: Bloqueio por Conflito e Sobreposição de Horários (Cenário Real do PBL)
**Regra do Documento:** O veículo `VL-01` já possui reserva no dia `18/08/2026` das `08:00` às `10:00` (Carlos Mendes). Outra equipe tenta agendar o mesmo carro das `09:00` às `11:00`.
1. Clique em **`+ Adicionar`** em **Reservas de Veículos**.
2. Preencha uma nova solicitação conflitante:
   - **Solicitante:** `Equipe de Logística` | **Setor:** `Operações`
   - **Atividade:** `Reunião Externa` | **Origem:** `Porto` | **Destino:** `Distrito Industrial`
   - **Data da Reserva:** `18/08/2026`
   - **Horário de Saída:** `09:00`
   - **Horário de Retorno:** `11:00`
   - **Quantidade de Passageiros:** `2`
   - **Veículo Solicitado:** Selecione `VL-01 - Fiat Cronos 1.3`
3. Clique em **SALVAR**.
> **Resultado na tela:** A interface **bloqueia o salvamento** e exibe um alerta vermelho em destaque:  
> ⚠️ *"Conflito de agenda: o veículo VL-01 já possui a Reserva #1 confirmada para 18/08/2026 das 08:00 às 10:00 (solicitante: Carlos Mendes - Coord. Financeira)."*

---

### 🔹 Teste 4: Liberação de Uso em Horário Posterior (Sem Conflito — Caso do PBL)
**Regra do Documento:** O veículo `VL-01` conclui sua viagem anterior às `10:00`. Uma solicitação para as `10:30` às `12:00` na mesma data deve ser aceita normalmente.
1. No mesmo formulário de reserva para o veículo `VL-01` em `18/08/2026`:
   - Altere o **Horário de Saída** para `10:30`
   - Altere o **Horário de Retorno** para `12:00`
2. Clique em **SALVAR**.
> **Resultado na tela:** O sistema valida que o veículo já terá retornado e **salva a reserva com sucesso**!

---

### 🔹 Teste 5: Rejeição por Lotação Excedida (Caso Real do PBL: 7 pessoas em carro de 4 lugares)
**Narrativa do Documento:** Uma equipe tenta embarcar 7 passageiros em um carro leve de apenas 4 lugares.
1. Clique em **`+ Adicionar`** em **Reservas de Veículos**.
2. Preencha os campos básicos e selecione o veículo `VL-02` (Categoria Leve - 4 lugares).
3. No campo **Quantidade de Passageiros**, digite: `7`.
4. Clique em **SALVAR**.
> **Resultado na tela:** A interface barra o pedido com a mensagem em vermelho:  
> ⚠️ *"O veículo selecionado (VL-02 - Chevrolet Onix Plus) comporta até 4 passageiros, mas foram solicitadas 7 vagas."*

---

### 🔹 Teste 6: Rejeição por Limite Global Máximo do Sistema (> 18 Passageiros)
**Regra do Documento:** Nenhuma viagem pode ultrapassar o teto máximo de 18 passageiros do COSEG.
1. Clique em **`+ Adicionar`** em **Reservas de Veículos**.
2. Selecione o veículo coletivo `VC-01 - Mercedes-Benz Sprinter`.
3. No campo **Quantidade de Passageiros**, digite: `22`.
4. Clique em **SALVAR**.
> **Resultado na tela:** A interface bloqueia:  
> ⚠️ *"Capacidade máxima do sistema COSEG excedida (22 pessoas). O sistema comporta no máximo 18 passageiros por viagem."*

---

### 🔹 Teste 7: Rejeição por Horário Inconsistente (Retorno Anterior à Saída)
1. Tente cadastrar uma reserva com:
   - **Horário de Saída:** `15:00`
   - **Horário de Retorno:** `14:00` (ou `15:00`)
2. Clique em **SALVAR**.
> **Resultado na tela:**  
> ⚠️ *"Horário inválido: o retorno (14:00) deve ser estritamente posterior ao horário de saída (15:00)."*

---

### 🔹 Teste 8: Rejeição por Data no Passado
1. Tente cadastrar uma reserva com data anterior à de hoje (ex: `10/01/2020`).
2. Clique em **SALVAR**.
> **Resultado na tela:**  
> ⚠️ *"A data da reserva não pode estar no passado."*

---

### 🔹 Teste 9: Modificar Dados e Cancelar Reserva no Sistema
1. Na lista de **Reservas de Veículos**, clique em qualquer reserva existente para editá-la.
2. Altere informações (ex: mude a atividade ou o destino).
3. Para **Cancelar a Viagem**: altere o campo **Status da Reserva** para `Cancelada` e clique em **Salvar**.
> **Resultado na tela:** O status muda para cancelada e o veículo fica imediatamente liberado para atender outras demandas naquele horário.

---

### 🌐 Consultas Diretas no Navegador (API JSON)
Com o `runserver` ligado, você também pode abrir as seguintes URLs diretamente na barra do seu navegador para conferir as respostas em JSON puro:
- 📄 `http://127.0.0.1:8000/` — Catálogo e status do servidor.
- 🚗 `http://127.0.0.1:8000/veiculos/` — Listagem da frota oficial e capacidades.
- 📅 `http://127.0.0.1:8000/reservas/` — Reservas confirmadas registradas no banco.
