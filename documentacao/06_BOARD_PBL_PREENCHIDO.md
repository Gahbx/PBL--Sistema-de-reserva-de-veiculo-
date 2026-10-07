# 06 - Resolução Completa do Board de Tutoria (PBL 1 - Agenda em Conflito)

Este documento contém o preenchimento oficial e fundamentado do **Board de Tutoria da Metodologia PBL** (Problema 1: *Agenda em Conflito — Sistema COSEG de Reserva de Veículos do Porto do Itaqui*), estruturado de acordo com o modelo padrão da **UNDB**.

---

## 📌 Visão Geral do Board

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 BOARD DE TUTORIA PBL - UNDB                                     │
│                     Problema 1 · Agenda em Conflito (Reserva de Veículos)                        │
├──────────────────┬──────────────────┬─────────────────────────────┬──────────────────────────────┤
│ 1. TERMOS        │ 2. CONCEITOS     │ 3. EXPLICAÇÃO               │ 4. PROBLEMA                  │
│    DESCONHECIDOS │    CONFUSOS      │    RESUMIDA                 │    CENTRAL                   │
├──────────────────┼──────────────────┼─────────────────────────────┼──────────────────────────────┤
│ 5. CAUSAS DO     │ 6. EFEITOS DO    │ 7. OBJETIVOS DE             │ 8. SOLUÇÃO DE                │
│    PROBLEMA      │    PROBLEMA      │    APRENDIZAGEM             │    CADA QUESTÃO              │
└──────────────────┴──────────────────┴─────────────────────────────┴──────────────────────────────┘
```

---

## 1. Termos Desconhecidos

1. **COSEG (Coordenação de Segurança e Serviços Gerais):**
   - *Significado:* Setor administrativo e operacional do Porto do Itaqui encarregado da gestão patrimonial, segurança predial e gerenciamento logístico da frota de transporte corporativo.
   - *Importância no problema:* É o setor que concentra as demandas e que atualmente sofre com a falta de um sistema centralizado de controle.
2. **Porto do Itaqui:**
   - *Significado:* Complexo portuário público de grande relevância nacional localizado em São Luís (MA), operando granéis líquidos, sólidos e cargas gerais.
   - *Importância no problema:* A extensão do porto e suas demandas operacionais contínuas tornam o transporte interno e externo um recurso crítico que não pode sofrer atrasos.
3. **Frota Corporativa Compartilhada:**
   - *Significado:* Conjunto de veículos patrimoniais pertencentes à organização disponibilizados para atender diferentes colaboradores e setores sob demanda rotativa.
4. **Sobreposição de Horários (Conflito de Agenda):**
   - *Significado:* Situação em que dois ou mais agendamentos para o mesmo veículo na mesma data possuem interseção nos seus intervalos de utilização.
5. **Django ORM (Object-Relational Mapping):**
   - *Significado:* Mapeador Objeto-Relacional do framework Django que permite interagir com tabelas de banco de dados SQL através de classes e objetos em linguagem Python.
6. **Migrations:**
   - *Significado:* Arquivos gerados pelo Django que traduzem alterações nos modelos Python (`models.py`) em comandos estruturais DDL no banco de dados relacional.
7. **CRUD (Create, Read, Update, Delete):**
   - *Significado:* As quatro operações essenciais de manipulação de dados em sistemas computacionais: Criação, Leitura/Consulta, Atualização e Exclusão.

---

## 2. Conceitos Confusos

1. **Validação na Camada de Servidor (Back-end) vs Validação na Interface (Front-end):**
   - *Esclarecimento:* A interface Web auxilia o usuário preenchendo máscaras e avisos visuais, mas **o servidor é a autoridade única e indispensável**. Se a validação não estiver no back-end, dados inválidos ou conflitantes podem ser gravados diretamente no banco.
2. **Controle de Intervalo Completo vs Registro Apenas do Horário de Saída:**
   - *Esclarecimento:* Registrar apenas a saída cria um "ponto cego". O conflito frequentemente acontece porque o veículo previsto para retornar às 14h foi agendado para outra equipe às 14h sem considerar o tempo real de volta e eventuais atrasos de trânsito.
3. **Capacidade Máxima Geral do Sistema vs Lotação do Veículo Selecionado:**
   - *Esclarecimento:* O sistema tem capacidade teto de 18 passageiros (atendida pelos veículos coletivos `VC-01` e `VC-02`), mas veículos leves (`VL-01` a `VL-08`) suportam no máximo 4 passageiros. Ambas as regras devem coexistir: não aceitar mais de 18 no geral, e não aceitar mais passageiros do que o veículo escolhido comporta.
4. **`makemigrations` vs `migrate`:**
   - *Esclarecimento:* `makemigrations` analisa o arquivo `models.py` e cria o script em Python que descreve o que mudou. `migrate` pega essas migrações e executa o código SQL de criação/alteração das tabelas no banco SQLite.
5. **Model Django vs Tabela do Banco de Dados:**
   - *Esclarecimento:* O Model é uma classe em código Python. A tabela é a estrutura física de linhas e colunas salva dentro do arquivo do banco `db.sqlite3`.

---

## 3. Explicação Resumida (Fatos do Cenário)

- O Porto do Itaqui possui uma rotina intensa com demandas logísticas, vistorias técnicas, treinamentos e compromissos institucionais.
- A frota é finita e composta por **10 veículos oficiais**: 8 veículos leves (capacidade para até 4 passageiros) e 2 coletivos (capacidade para até 18 passageiros).
- As solicitações chegavam de forma fragmentada por ligações, mensagens de WhatsApp, e-mails ou pedidos de balcão, sendo anotadas em agendas físicas ou planilhas locais.
- A conferência dependia exclusivamente da memória humana dos funcionários do COSEG, gerando falhas críticas:
  - Duas equipes disputando o mesmo carro no mesmo horário para atividades distintas.
  - Solicitação de 7 passageiros para um veículo leve de 4 lugares, percebida apenas na hora da partida.
  - Agendamento de uma viagem no mesmo horário de retorno de outra equipe, sem intervalo de segurança.
- A direção determinou a criação de uma camada de servidor centralizada em Python/Django que seja a fonte da verdade para armazenar as reservas e garantir o cumprimento de todas as regras.

---

## 4. Problema Central

> **"Inexistência de um sistema computacional centralizado, confiável e automatizado para o gerenciamento de reservas da frota do COSEG, resultando em registros dispersos, conflitos de horário, dimensionamento inadequado da capacidade de veículos e atrasos operacionais no Porto do Itaqui."**

---

## 5. Causas do Problema

1. **Dispersão e Descentralização dos Canais de Entrada:** Ausência de um canal único para submissão de pedidos (solicitações via telefone, e-mail e mensagens informais).
2. **Processo Manual e Dependente de Memória:** Registros efetuados em planilhas não integradas, cadernos de anotações ou dependentes da lembrança dos funcionários.
3. **Ausência de Validações Automatizadas:** Falta de regras de sistema para impedir solicitações com capacidade incompatível ou datas incorretas.
4. **Desconsideração do Horário de Retorno:** Registro restrito ao momento de saída, sem travar o intervalo total de indisponibilidade do veículo.
5. **Inexistência de Banco de Dados Relacional:** Ausência de uma fonte única e persistente da verdade consultável em tempo real.

---

## 6. Efeitos do Problema

1. **Atrasos e Interrupção de Atividades Portuárias:** Equipes paradas na portaria sem conseguir se deslocar para vistorias ou reuniões externas.
2. **Conflito Interdepartamental e Desgaste Institucional:** Atrito entre colaboradores de diferentes setores disputando a chave do mesmo veículo.
3. **Inviabilidade de Transporte de Passageiros:** Equipes de 7 colaboradores não conseguindo embarcar em veículos de 4 passageiros, com constrangimento e retrabalho na saída.
4. **Desorientação dos Motoristas:** Condutores recebendo ordens contraditórias sobre qual setor ou destino atender prioritariamente.
5. **Retrabalho e Sobrecarga no COSEG:** Perda de tempo na reorganização emergencial de escala de motoristas e busca de veículos reservas.

---

## 7. Objetivos de Aprendizagem

1. **Como modelar entidades de domínio (Veículo e Reserva) utilizando o Django ORM e relacionamentos de chave estrangeira?**
2. **De que forma o servidor HTTP em Django (URLs, Views e Serviços) deve interceptar e validar dados antes da persistência no banco de dados?**
3. **Como formular e implementar um algoritmo de detecção de sobreposição de horários para evitar conflitos de agenda no compartilhamento de recursos?**
4. **Como estruturar operações completas de CRUD (Create, Read, Update, Delete) em conformidade com as boas práticas de Engenharia de Software?**
5. **Como planejar e disponibilizar endpoints de servidor (API JSON) confiáveis para integração com a interface Web do PBL 2?**

---

## 8. Solução de cada Questão (Implementação Técnica Realizada)

| Questão / Demanda do PBL | Solução Técnica Implementada no Projeto |
| :--- | :--- |
| **Persistência Centralizada da Frota** | Criação do model `Veiculo` no Django ORM (`reservas/models.py`) com persistência em SQLite, contemplando os 8 veículos leves (4 lugares) e 2 coletivos (18 lugares). |
| **Estrutura Completa de Dados da Reserva** | Criação do model `Reserva` armazenando: solicitante, setor, atividade, origem, destino, data, horário de saída, horário de retorno, passageiros, veículo vinculado e observações. |
| **Controle de Capacidade dos Veículos** | Validação em `services.py` bloqueando pedidos acima de 18 passageiros ou que superem a capacidade individual do carro (ex: 7 em veículo de 4). |
| **Consistência de Horários e Datas** | Bloqueio de reservas com datas no passado (`data < timezone.localdate()`) e exigência de que `horario_retorno > horario_saida`. |
| **Algoritmo Anticonflito de Agenda** | Aplicação da fórmula de sobreposição: `(nova_saida < retorno_existente) and (nova_retorno > saida_existente)` para o mesmo veículo na mesma data. |
| **Operações CRUD Completas** | Endpoints HTTP em `views.py` permitindo Criar (`POST /reservas/`), Consultar (`GET /reservas/`), Atualizar (`PUT /reservas/<id>/`) e Cancelar (`DELETE /reservas/<id>/`). |
| **Disponibilização de API para o PBL 2** | Retorno padronizado em formato JSON com status HTTP adequados (`200`, `201`, `400`, `404`) e mensagens claras de sucesso ou erro. |
| **Garantia de Qualidade e Evidências** | Bateria de **18 testes automatizados** em `reservas/tests.py`, incluindo os 4 dados iniciais fornecidos pelo COSEG e testes de colisão de horários. |

---

*Documento elaborado para a tutoria do PBL 1 — Programação para Web (UNDB / Prof. Me. Danilo Costa).*
