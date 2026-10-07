# 02 - Estrutura de Pastas e Explicação de Cada Arquivo

Este documento foi criado especialmente para explicar, de forma **didática, simples e intuitiva**, como o projeto está organizado, o papel de cada pasta raiz e o que cada arquivo faz.

---

## 📂 Visão Geral da Árvore de Diretórios

```text
Reserva de veiculo/
│
├── manage.py                          # Utilitário de linha de comando do Django
├── db.sqlite3                         # Arquivo do banco de dados relacional SQLite
├── requirements.txt                   # Arquivo com as bibliotecas Python necessárias
│
├── coseg_mobilidade/                  # PASTA RAIZ 1: Configuração global do projeto Django
│   ├── __init__.py                    # Indica que a pasta é um pacote Python
│   ├── settings.py                    # Configurações gerais (apps, fuso horário, banco)
│   ├── urls.py                        # Roteador principal de URLs do servidor
│   ├── wsgi.py                        # Ponto de entrada para servidores WSGI tradicionais
│   └── asgi.py                        # Ponto de entrada para servidores assíncronos ASGI
│
├── reservas/                          # PASTA RAIZ 2: Aplicativo central de regras de reservas
│   ├── __init__.py                    # Indica pacote Python
│   ├── apps.py                        # Configuração de registro do app no Django
│   ├── admin.py                       # Configuração do painel administrativo Django Admin
│   ├── models.py                      # Modelagem das tabelas do banco (Veiculo e Reserva)
│   ├── services.py                    # Camada de Regras de Negócio (capacidade, horários, conflitos)
│   ├── views.py                       # Controladores / Endpoints da API JSON (CRUD completo)
│   ├── urls.py                        # Rotas e caminhos específicos do app reservas
│   ├── tests.py                       # Suíte com 18 testes automatizados para o PBL
│   │
│   ├── migrations/                    # Subpasta: Histórico de migrações do banco
│   │   ├── __init__.py
│   │   └── 0001_initial.py            # Script que gerou as tabelas Veiculo e Reserva no banco
│   │
│   └── management/                    # Subpasta: Comandos customizados do terminal
│       └── commands/
│           ├── __init__.py
│           └── popular_banco.py       # Script "popular_banco" para cadastrar a frota e dados do PBL
│
└── documentacao/                      # PASTA RAIZ 3: Guias e documentação completa
    ├── 01_VISAO_GERAL_E_COMO_EXECUTAR.md
    ├── 02_ESTRUTURA_DAS_PASTAS_E_ARQUIVOS.md
    ├── 03_REGRAS_DE_NEGOCIO_E_LOGICA_DO_PROBLEMA.md
    ├── 04_GUIA_DAS_ROTAS_E_API_JSON.md
    └── 05_EVIDENCIAS_DOS_TESTES_E_AVALIACAO.md
```

---

## 🔍 Detalhamento das Pastas Raiz

### 1. `coseg_mobilidade/` (Configuração Global do Projeto)
Esta pasta foi gerada pelo Django para abrigar as configurações centrais do sistema.

- **`settings.py`**: É o cérebro das configurações do sistema.
  - Registra o app `'reservas.apps.ReservasConfig'` na lista `INSTALLED_APPS`.
  - Configura o idioma para o português do Brasil (`LANGUAGE_CODE = 'pt-br'`).
  - Configura o fuso horário oficial para o horário de Brasília (`TIME_ZONE = 'America/Sao_Paulo'`).
  - Define o banco de dados como SQLite (`db.sqlite3`).
- **`urls.py`**: É a portaria do sistema. Ele recebe todas as requisições que chegam no servidor e repassa para o arquivo de rotas específico do app `reservas` através do comando `include('reservas.urls')`.
- **`wsgi.py` / `asgi.py`**: São interfaces padrão do Python para publicação do sistema em servidores de produção na nuvem.

---

### 2. `reservas/` (O Núcleo da Aplicação)
Esta pasta representa o aplicativo Django responsável por todo o domínio do problema do COSEG.

- **`models.py` (Camada de Dados / Django ORM)**:
  - Define as classes `Veiculo` e `Reserva`, que o Django transforma automaticamente em tabelas no SQLite.
  - `Veiculo`: guarda `codigo` (ex: "VL-01"), `modelo`, `categoria` (Leve ou Coletivo), `capacidade` (4 ou 18) e status `ativo`.
  - `Reserva`: guarda `solicitante`, `setor`, `atividade`, `origem`, `destino`, `data`, `horario_saida`, `horario_retorno`, `quantidade_passageiros`, `veiculo` (relação ForeignKey com o veículo) e `status`.
  - Possui o método `clean()` que garante que nenhuma reserva seja gravada com erros de regra de negócio.

- **`services.py` (Camada de Regras de Negócio e Lógica Limpa)**:
  - Separado de propósito para deixar o código fácil de entender.
  - Contém a função pura `verificar_sobreposicao_horarios()` que implementa a fórmula matemática de conflito de intervalos.
  - Contém `buscar_reservas_conflitantes()` que consulta o banco via Django ORM para saber se o veículo já está ocupado.
  - Contém `validar_regras_reserva()` que valida capacidade, data no passado e horários.

- **`views.py` (Camada de Servidor / Endpoints JSON)**:
  - Recebe requisições HTTP (`GET`, `POST`, `PUT`, `DELETE`).
  - Lê os dados enviados no corpo da requisição (JSON).
  - Aciona os serviços e o Django ORM.
  - Devolve respostas estruturadas em formato `JsonResponse` com códigos de status HTTP apropriados (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`).

- **`urls.py` (Mapeamento de Rotas do App)**:
  - Conecta caminhos de texto (ex: `veiculos/`, `reservas/`, `reservas/verificar-conflito/`) diretamente com as funções do `views.py`.

- **`tests.py` (Garantia de Qualidade e Evidências)**:
  - Contém 18 testes automatizados que comprovam para o professor que todas as exigências do PDF foram implementadas com rigor e funcionam perfeitamente.

- **`admin.py` (Painel Administrativo)**:
  - Registra os modelos `Veiculo` e `Reserva` no painel administrativo nativo do Django para consulta rápida com filtros e buscas.

---

### 3. `reservas/management/commands/` (Comandos Customizados)
- **`popular_banco.py`**:
  - Permite rodar `python manage.py popular_banco`.
  - Cria automaticamente os 10 veículos da frota (8 leves e 2 coletivos) e as 4 reservas de teste oficiais solicitadas pelo professor.

---

### 4. Arquivos na Raiz do Projeto
- **`manage.py`**: O script utilitário do Django usado para rodar comandos no terminal como `migrate`, `runserver`, `test` e `popular_banco`.
- **`db.sqlite3`**: O arquivo físico do banco de dados relacional. Ele guarda de forma persistente todos os veículos e reservas.
- **`requirements.txt`**: Lista as dependências do projeto (Django).
