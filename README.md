# 🚗 COSEG Mobilidade — Sistema de Reserva de Veículos (Porto do Itaqui)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B-green.svg)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/Banco-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Status-100%25%20Funcional-brightgreen.svg)]()
[![Testes](https://img.shields.io/badge/Testes-18%20Aprovados-success.svg)]()

> **Projeto Acadêmico:** Metodologia Ativa PBL 1 (Problema 1: *Agenda em Conflito*)  
> **Instituição:** UNDB — Centro Universitário  
> **Curso:** Engenharia de Software / Ciência da Computação (5º Período — 2026.2)  
> **Disciplina:** Programação para Web | **Docente:** Prof. Me. Danilo Costa  
> **Escopo da Etapa 01 e 02:** Camada de Servidor (Back-end puro em Python/Django com banco relacional e API JSON).

---

## 📖 1. Sobre o Projeto

O setor **COSEG** (Coordenação de Segurança e Serviços Gerais) do **Porto do Itaqui** gerencia uma frota corporativa compartilhada de **10 veículos** (8 leves e 2 coletivos). Devido a processos manuais, registros dispersos em planilhas e comunicação via telefone/WhatsApp, a empresa enfrentava conflitos críticos de agenda, falhas de dimensionamento de capacidade e desorientação de motoristas.

Esta solução implementa a **Camada de Servidor (Back-end)** completa da aplicação, centralizando as regras de negócio e atuando como a fonte única da verdade para consultas e persistência de dados.

### 🛡️ Regras de Negócio Implementadas no Servidor:
1. **Capacidade por Categoria:**
   - Veículos Leves (`VL-01` a `VL-08`): capacidade de até **4 passageiros**.
   - Veículos Coletivos (`VC-01` e `VC-02`): capacidade de até **18 passageiros**.
   - Rejeição obrigatória para qualquer solicitação com **mais de 18 passageiros**.
   - Rejeição quando a quantidade solicitada exceder a lotação do veículo escolhido (ex: 7 pessoas em veículo de 4 lugares).
2. **Consistência de Horários:**
   - O horário de retorno deve ser **estritamente posterior** ao horário de saída.
3. **Validação de Data:**
   - Bloqueio de reservas agendadas em datas no passado.
4. **Algoritmo Anticonflito (Sobreposição de Horários):**
   - Aplica a fórmula matemática de interseção temporal para o mesmo veículo na mesma data:
     $$\text{Sobreposição} \iff (\text{saida}_{\text{nova}} < \text{retorno}_{\text{existente}}) \land (\text{retorno}_{\text{nova}} > \text{saida}_{\text{existente}})$$
5. **Persistência Relacional:**
   - Mapeamento objeto-relacional (Django ORM) no banco SQLite com operações completas de CRUD.

---

## 💻 2. Requisitos de Ambiente (O que você precisa ter)

Antes de começar, verifique se possui instalado em sua máquina:

- **Python** (versão 3.10 ou superior recomendada):
  - [Download do Python](https://www.python.org/downloads/)
  - *No Windows, certifique-se de marcar a opção "Add Python to PATH" durante a instalação.*
- **Git** (para controle de versão):
  - [Download do Git](https://git-scm.com/downloads)
- **Gerenciador de Pacotes pip** (já vem instalado com o Python).

---

## 🚀 3. Guia de Instalação e Execução Passo a Passo

Abra o seu terminal (Prompt de Comando, PowerShell ou Terminal do VS Code) e siga as etapas abaixo:

### Passo 1: Obter o projeto
Se você clonou via Git:
```bash
git clone <URL_DO_REPOSITORIO>
cd "Reserva de veiculo"
```
Ou simplesmente navegue até a pasta onde o projeto está salvo:
```bash
cd "c:\Users\gabri\OneDrive\Desktop\Reserva de veiculo"
```

---

### Passo 2: Criar e Ativar um Ambiente Virtual (Recomendado)
O ambiente virtual isola as bibliotecas do projeto:

* **No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(Se houver erro de política de execução no PowerShell, execute `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`)*

* **No Windows (CMD / Prompt de Comando):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

* **No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Passo 3: Instalar as Dependências do Projeto
Com o ambiente ativado, instale as bibliotecas requeridas:
```bash
pip install -r requirements.txt
```

---

### Passo 4: Aplicar as Migrações do Banco de Dados
Gera e configura o banco relacional SQLite local (`db.sqlite3`):
```bash
python manage.py migrate
```

---

### Passo 5: Popular a Frota e os Dados Oficiais de Teste do PBL
Executa o comando automatizado que cadastra a frota de 10 veículos e as 4 reservas fornecidas pelo COSEG no documento do PBL:
```bash
python manage.py popular_banco
```
*Saída esperada:*
```text
===> Inicializando cadastro da frota oficial do COSEG...
Frota cadastrada com sucesso (10 veículos no total)!
Reservas de teste do COSEG cadastradas com sucesso (4 novas)!
Banco de dados pronto para testes e simulações do PBL 1!
```

---

### Passo 6: Executar a Suíte de Testes Automatizados (Evidência Formal)
Para comprovar que todas as regras de negócio e validações de conflito estão funcionando com 100% de precisão:
```bash
python manage.py test -v 2
```
*Resultado:* **18 testes executados e aprovados** com sucesso (`OK`).

---

### Passo 7: Iniciar o Servidor de Desenvolvimento
Inicie a aplicação localmente:
```bash
python manage.py runserver
```
O servidor estará disponível no endereço:
👉 **`http://127.0.0.1:8000/`**

---

## 🔀 4. Versionamento com Git (Guia de Comandos)

Para versionar este projeto e sincronizá-lo com um repositório remoto (como GitHub ou GitLab), utilize o fluxo padrão:

### 1. Inicializar o repositório local:
```bash
git init
```

### 2. Verificar arquivos modificados:
```bash
git status
```

### 3. Adicionar arquivos ao controle de versão:
```bash
git add .
```

### 4. Criar o commit com mensagem semântica:
```bash
git commit -m "feat: implementacao completa da camada de servidor em django para o pbl 1"
```

### 5. Configurar a branch principal e conectar ao repositório remoto:
```bash
git branch -M main
git remote add origin https://github.com/Gahbx/PBL--Sistema-de-reserva-de-veiculo-.git
git push -u origin main
```

### Boas Práticas de Mensagens de Commit Utilizadas:
- `feat:` Inclusão de nova funcionalidade ou endpoint.
- `fix:` Correção de regras de validação ou bugs.
- `docs:` Criação ou atualização de documentações e Board de tutoria.
- `test:` Inclusão ou modificação da bateria de testes automatizados.
- `refactor:` Melhoria de código sem alterar o comportamento externo.

---

## 📡 5. Catálogo de Rotas e Endpoints da API JSON

A Camada de Servidor responde em formato `JSON` com status HTTP padronizados (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`).

| Método | Endpoint | Função / Descrição |
| :---: | :--- | :--- |
| `GET` | `/` | Apresentação do servidor e catálogo de rotas disponíveis |
| `GET` | `/veiculos/` | Lista a frota cadastrada, capacidades e status de atividade |
| `POST` | `/veiculos/` | Cadastra um novo veículo na frota |
| `GET` | `/veiculos/<codigo>/` | Detalhes de um veículo específico e histórico de viagens |
| `GET` | `/reservas/` | Lista reservas registradas (filtros por `?data=`, `?veiculo=`, `?status=`) |
| `POST` | `/reservas/` | Registra uma nova reserva aplicando todas as validações |
| `GET` | `/reservas/<id>/` | Consulta detalhes completos de uma reserva específica |
| `PUT` | `/reservas/<id>/` | Atualiza uma reserva existente (revalidando conflitos) |
| `DELETE` | `/reservas/<id>/` | Cancela (`status=CANCELADA`) ou remove uma reserva |
| `POST` | `/reservas/verificar-conflito/` | Endpoint prévio para simular e checar disponibilidade de horário |

### Exemplo de Teste no Terminal (PowerShell):
```powershell
# Consultar catálogo inicial
Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method GET

# Listar frota de veículos
Invoke-RestMethod -Uri "http://127.0.0.1:8000/veiculos/" -Method GET

# Simular conflito em tempo real
$body = @{
    veiculo = "VL-01"
    data = "2026-08-18"
    horario_saida = "09:00"
    horario_retorno = "11:00"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/reservas/verificar-conflito/" -Method POST -Body $body -ContentType "application/json"
```

---

## 📂 6. Estrutura de Pastas e Documentação

Para consultar detalhes aprofundados sobre a arquitetura do projeto e o processo de aprendizagem, explore a pasta [`documentacao/`](./documentacao/):

- 📄 [01_VISAO_GERAL_E_COMO_EXECUTAR.md](./documentacao/01_VISAO_GERAL_E_COMO_EXECUTAR.md): Introdução técnica e passo a passo operacional.
- 📄 [02_ESTRUTURA_DAS_PASTAS_E_ARQUIVOS.md](./documentacao/02_ESTRUTURA_DAS_PASTAS_E_ARQUIVOS.md): Explicação didática de cada pasta raiz e de cada arquivo.
- 📄 [03_REGRAS_DE_NEGOCIO_E_LOGICA_DO_PROBLEMA.md](./documentacao/03_REGRAS_DE_NEGOCIO_E_LOGICA_DO_PROBLEMA.md): Lógica matemática de sobreposição e regras do COSEG.
- 📄 [04_GUIA_DAS_ROTAS_E_API_JSON.md](./documentacao/04_GUIA_DAS_ROTAS_E_API_JSON.md): Guia de integração da API RESTful para o PBL 2.
- 📄 [05_EVIDENCIAS_DOS_TESTES_E_AVALIACAO.md](./documentacao/05_EVIDENCIAS_DOS_TESTES_E_AVALIACAO.md): Matriz de evidências e resultados dos 18 testes automatizados.
- 📄 [06_BOARD_PBL_PREENCHIDO.md](./documentacao/06_BOARD_PBL_PREENCHIDO.md): Resolução completa das 8 etapas do Board de Tutoria da Metodologia PBL.

Além disso, o arquivo do **Board em PowerPoint** preenchido está disponível em:
- 📊 [`Fontes/Board_PBL_Problema_1_reserva_veiculos.pptx`](./Fontes/Board_PBL_Problema_1_reserva_veiculos.pptx)

---

## 👥 Autoria e Agradecimentos

- **Instituição:** UNDB — Centro Universitário
- **Disciplina:** Programação para Web (PBL 1)
- **Docente Orientador:** Prof. Me. Danilo Costa
