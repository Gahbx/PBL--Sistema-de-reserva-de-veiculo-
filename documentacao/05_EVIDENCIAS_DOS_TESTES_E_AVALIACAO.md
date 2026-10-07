# 05 - Evidências dos Testes Automatizados e Apresentação da Solução

O documento de orientações do PBL 1 especifica como uma das principais entregas:
> *"Evidências dos testes de persistência, CRUD, capacidade e conflito de horários."*

Para comprovar formalmente o atendimento a cada critério avaliativo, o arquivo `reservas/tests.py` conta com **18 testes automatizados** integrados ao framework de testes do Django.

---

## 🧪 Como Rodar os Testes no Terminal

Execute o comando padrão do Django:
```powershell
python manage.py test
```

Para visualizar cada teste sendo executado individualmente com seus respectivos nomes detalhados (modo verboso), execute:
```powershell
python manage.py test -v 2
```

---

## 📊 Matriz de Rastreabilidade de Testes

| Classe de Teste | Método de Teste | Exigência do PBL Coberta |
| :--- | :--- | :--- |
| **TestFrotaVeiculos** | `test_persistencia_veiculo` | Persistência da frota leve (capacidade 4) no banco SQLite via ORM |
| **TestFrotaVeiculos** | `test_veiculo_coletivo_capacidade` | Persistência de veículo coletivo (capacidade 18) |
| **TestRegrasDeNegocio** | `test_rejeicao_acima_de_18_passageiros` | Rejeição de solicitações acima de 18 passageiros (teto máximo) |
| **TestRegrasDeNegocio** | `test_rejeicao_capacidade_excedida_veiculo_leve` | Rejeição quando passageiros > capacidade do veículo (ex: 7 em carro de 4) |
| **TestRegrasDeNegocio** | `test_rejeicao_horario_retorno_invalido` | Bloqueio de horário de retorno menor ou igual ao de saída |
| **TestRegrasDeNegocio** | `test_rejeicao_data_no_passado` | Bloqueio de agendamento em datas anteriores à data de hoje |
| **TestDetecaoConflitoHorarios** | `test_formula_matematica_sobreposicao` | Validação matemática da fórmula de interseção de intervalos temporais |
| **TestDetecaoConflitoHorarios** | `test_cenario_conflito_do_documento_pbl` | Cenário do PBL: Reserva das 08h-10h colidindo com nova das 09h-11h |
| **TestDetecaoConflitoHorarios** | `test_cenario_sem_conflito_do_documento_pbl` | Cenário do PBL: Reserva das 08h-10h sem colisão com nova das 10h30-12h |
| **TestCenariosOficiaisCOSEG** | `test_todas_as_reservas_iniciais_persistidas` | Gravação das 4 reservas oficiais de exemplo fornecidas pelo COSEG |
| **TestCenariosOficiaisCOSEG** | `test_conflito_com_reserva_do_enunciado` | Tentativa de conflito com a reserva oficial do VL-01 em 18/08/2026 |
| **TestCenariosOficiaisCOSEG** | `test_sucesso_sem_conflito_com_reserva_do_enunciado` | Agendamento válido adjacente à reserva oficial do VL-01 |
| **TestEndpointsAPI** | `test_api_catalogo_index` | Disponibilidade da rota raiz `GET /` com catálogo de endpoints |
| **TestEndpointsAPI** | `test_api_listar_veiculos` | Operação READ da frota via JSON (`GET /veiculos/`) |
| **TestEndpointsAPI** | `test_api_criar_reserva_sucesso_crud_create` | Operação CREATE do CRUD com status HTTP `201 Created` |
| **TestEndpointsAPI** | `test_api_criar_reserva_rejeitada_por_conflito` | Rejeição na API com status HTTP `400 Bad Request` por conflito de horário |
| **TestEndpointsAPI** | `test_api_reserva_crud_read_update_delete` | Ciclo completo do CRUD: leitura individual, atualização e cancelamento |
| **TestEndpointsAPI** | `test_api_verificar_conflito_endpoint` | Endpoint de simulação preventiva de conflitos |

---

## ✅ Evidência de Execução Real

```text
Creating test database for alias 'default'...
test_persistencia_veiculo (reservas.tests.TestFrotaVeiculos) ... ok
test_veiculo_coletivo_capacidade (reservas.tests.TestFrotaVeiculos) ... ok
test_rejeicao_acima_de_18_passageiros (reservas.tests.TestRegrasDeNegocioValidacoes) ... ok
test_rejeicao_capacidade_excedida_veiculo_leve (reservas.tests.TestRegrasDeNegocioValidacoes) ... ok
test_rejeicao_data_no_passado (reservas.tests.TestRegrasDeNegocioValidacoes) ... ok
test_rejeicao_horario_retorno_invalido (reservas.tests.TestRegrasDeNegocioValidacoes) ... ok
test_cenario_conflito_do_documento_pbl (reservas.tests.TestDetecaoConflitoHorarios) ... ok
test_cenario_sem_conflito_do_documento_pbl (reservas.tests.TestDetecaoConflitoHorarios) ... ok
test_formula_matematica_sobreposicao (reservas.tests.TestDetecaoConflitoHorarios) ... ok
test_conflito_com_reserva_do_enunciado (reservas.tests.TestCenariosOficiaisCOSEG) ... ok
test_sucesso_sem_conflito_com_reserva_do_enunciado (reservas.tests.TestCenariosOficiaisCOSEG) ... ok
test_todas_as_reservas_iniciais_persistidas (reservas.tests.TestCenariosOficiaisCOSEG) ... ok
test_api_catalogo_index (reservas.tests.TestEndpointsAPI) ... ok
test_api_criar_reserva_rejeitada_por_conflito (reservas.tests.TestEndpointsAPI) ... ok
test_api_criar_reserva_sucesso_crud_create (reservas.tests.TestEndpointsAPI) ... ok
test_api_listar_veiculos (reservas.tests.TestEndpointsAPI) ... ok
test_api_reserva_crud_read_update_delete (reservas.tests.TestEndpointsAPI) ... ok
test_api_verificar_conflito_endpoint (reservas.tests.TestEndpointsAPI) ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.056s

OK
Destroying test database for alias 'default'...
```
