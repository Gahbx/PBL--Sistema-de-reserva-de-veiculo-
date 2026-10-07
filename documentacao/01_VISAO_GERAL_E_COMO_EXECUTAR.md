# 01 - Visão Geral do Sistema COSEG Mobilidade e Guia de Execução

## 📌 1. Sobre o Projeto
Este projeto foi desenvolvido para atender aos requisitos da **Etapa 02 do PBL 1 — "Agenda em Conflito"** da disciplina **Programação para Web (5º Período de Engenharia de Software / Ciência da Computação - UNDB)**, ministrada pelo **Prof. Me. Danilo Costa**.

O setor **COSEG** do **Porto do Itaqui** enfrentava graves problemas operacionais devido a pedidos de veículos descentralizados (por telefone, e-mail e mensagens), resultando em:
1. **Conflito de agendas:** dois setores disputando o mesmo veículo no mesmo horário.
2. **Incompatibilidade de capacidade:** carros de 4 lugares solicitados para 7 pessoas.
3. **Não consideração do horário de retorno:** agendamentos subsequentes que não aguardavam a volta do veículo.

### 🎯 Foco desta Etapa (PBL 1)
> **Atenção pedagógica:** Conforme especificado pelo documento oficial do PBL 1, **esta entrega é 100% voltada à Camada de Servidor (Back-end em Python/Django)**. Não há HTML ou CSS nesta etapa. O objetivo é construir a base lógica de dados, persistência no SQLite, regras de negócio no servidor e endpoints de API RESTful em formato JSON prontos para serem consumidos pela interface Web que será desenvolvida no **PBL 2**.

---

## 🚀 2. Passo a Passo para Executar o Sistema

### Pré-requisitos
- Python 3.10 ou superior instalado no computador.
- Terminal (PowerShell, Prompt de Comando ou Git Bash).

---

### Passo 1: Abrir o terminal na pasta do projeto
Certifique-se de estar dentro do diretório do projeto:
```powershell
cd "c:\Users\gabri\OneDrive\Desktop\Reserva de veiculo"
```

---

### Passo 2: Instalar as dependências (se necessário)
```powershell
pip install -r requirements.txt
```

---

### Passo 3: Aplicar as Migrações do Banco de Dados
O Django criará automaticamente as tabelas no arquivo SQLite (`db.sqlite3`):
```powershell
python manage.py migrate
```

---

### Passo 4: Popular a Frota Oficial e os Dados Iniciais do PBL
Criamos um comando automatizado para cadastrar a **frota oficial de 10 veículos do COSEG** (8 veículos leves de 4 lugares e 2 coletivos de 18 lugares) e as **4 reservas de teste oficiais fornecidas pelo professor no enunciado**:
```powershell
python manage.py popular_banco
```
Você verá a mensagem de confirmação:
```text
===> Inicializando cadastro da frota oficial do COSEG...
Frota cadastrada com sucesso (10 veículos no total)!
Reservas de teste do COSEG cadastradas com sucesso (4 novas)!
Banco de dados pronto para testes e simulações do PBL 1!
```

---

### Passo 5: Rodar os Testes Automatizados (Evidência do PBL)
Para rodar a suíte completa de 18 testes automatizados que comprovam que todas as regras de negócio funcionam:
```powershell
python manage.py test
```
Saída esperada:
```text
Ran 18 tests in 0.056s
OK
```

---

### Passo 6: Iniciar o Servidor de Desenvolvimento
Inicie o servidor HTTP local do Django:
```powershell
python manage.py runserver
```
O servidor estará rodando em: `http://127.0.0.1:8000/`

Ao acessar `http://127.0.0.1:8000/` no navegador ou via Postman/Thunder Client/cURL, você receberá a resposta JSON com o catálogo de rotas e o status operacional do sistema.
