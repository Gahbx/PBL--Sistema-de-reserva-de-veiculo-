# 03 - Regras de Negócio e Lógica de Detecção de Conflitos

Neste documento, você encontra a explicação detalhada de cada regra de negócio extraída do documento oficial do PBL 1 e dos slides da **Aula 07 (Do Problema à Implementação Django)**, e como cada uma foi resolvida no código.

---

## 📋 As 5 Regras de Negócio Exigidas no PBL 1

### 🚗 Regra 1: Capacidade da Frota e Categorias
* **Texto do PBL:** *"Veículos leves transportam até quatro passageiros e veículos coletivos até dezoito; solicitações acima de dezoito passageiros devem ser rejeitadas ou sinalizadas."*
* **Implementação Técnica:**
  - Definimos no model `Veiculo` o campo `capacidade` (`4` para a categoria `LEVE` e `18` para a categoria `COLETIVO`).
  - No arquivo `reservas/services.py`, a função `validar_regras_reserva()` faz duas checagens complementares:
    1. Se `quantidade_passageiros > 18`: rejeita imediatamente com a mensagem `"Capacidade máxima do sistema COSEG excedida (X pessoas). O sistema comporta no máximo 18 passageiros por viagem."`
    2. Se `quantidade_passageiros > veiculo.capacidade`: rejeita com a mensagem `"O veículo selecionado (VL-XX) comporta até 4 passageiros, mas foram solicitadas X vagas."`

---

### 🕒 Regra 2: Consistência dos Horários (Saída vs Retorno)
* **Texto do PBL:** *"O horário de retorno deverá ser posterior ao horário de saída."*
* **Problema Relatado na Narrativa:** Solicitações que não previam retorno ou que colocavam o retorno antes/no mesmo horário da saída geravam confusão com os motoristas.
* **Implementação Técnica:**
  - O sistema compara os objetos de horário (`time`):
  ```python
  if horario_retorno <= horario_saida:
      erros['horario_retorno'] = (
          f"Horário inválido: o retorno ({horario_retorno}) deve ser "
          f"estritamente posterior ao horário de saída ({horario_saida})."
      )
  ```

---

### 📅 Regra 3: Bloqueio de Datas no Passado
* **Texto do PBL:** *"A data não poderá estar no passado."*
* **Implementação Técnica:**
  - O sistema obtém a data atual via `timezone.localdate()` (respeitando o fuso horário brasileiro de São Paulo) e impede qualquer data anterior:
  ```python
  if data < timezone.localdate():
      erros['data'] = f"A data da reserva ({data}) não pode estar no passado."
  ```

---

### ⚠️ Regra 4: Detecção Matemática de Conflitos e Sobreposição
* **Texto do PBL:** *"Existe conflito quando o veículo e a data são os mesmos e os períodos se sobrepõem. Por exemplo, uma reserva existente das 8h às 10h entra em conflito com uma nova reserva das 9h às 11h; uma nova reserva das 10h30 às 12h não apresenta sobreposição."*
* **A Fórmula de Interseção Temporal:**
  Dois intervalos temporais `A = [saida_A, retorno_A]` e `B = [saida_B, retorno_B]` colidem se, e somente se:
  $$\text{Sobreposição} \iff (\text{saida}_A < \text{retorno}_B) \land (\text{retorno}_A > \text{saida}_B)$$

#### 🔬 Demonstração Prática com os Exemplos do PBL:
Suponha uma reserva **existente no banco (A)**: das `08:00` às `10:00`.

1. **Cenário 1: Nova solicitação (B) das 09:00 às 11:00**
   - $\text{saida}_B < \text{retorno}_A \implies 09:00 < 10:00$ (**Verdadeiro**)
   - $\text{retorno}_B > \text{saida}_A \implies 11:00 > 08:00$ (**Verdadeiro**)
   - Ambas as condições são verdadeiras $\implies$ **CONFLITO DETECTADO (Rejeitado pelo servidor!)**

2. **Cenário 2: Nova solicitação (B) das 10:30 às 12:00**
   - $\text{saida}_B < \text{retorno}_A \implies 10:30 < 10:00$ (**Falso**)
   - Como a condição falha $\implies$ **SEM SOBREPOSIÇÃO (Aceito pelo servidor!)**

3. **Cenário 3: Nova solicitação (B) das 10:00 às 12:00**
   - $\text{saida}_B < \text{retorno}_A \implies 10:00 < 10:00$ (**Falso**, pois a saída coincide com o retorno da viagem anterior).
   - O veículo já terá retornado $\implies$ **SEM CONFLITO (Liberado para uso!)**

---

## 🗄️ Dados de Teste Oficiais Fornecidos pelo COSEG (Página 3 do PBL)

O documento do PBL forneceu 4 reservas oficiais que devem estar salvas no banco:

| Veículo | Categoria | Data | Horário | Finalidade / Atividade |
| :--- | :--- | :---: | :---: | :--- |
| **VL-01** | Leve (4 lug.) | 18/08/2026 | 08:00 às 10:00 | Reunião administrativa |
| **VL-03** | Leve (4 lug.) | 18/08/2026 | 13:00 às 15:00 | Inspeção técnica |
| **VC-01** | Coletivo (18 lug.) | 19/08/2026 | 09:00 às 12:00 | Treinamento |
| **VL-05** | Leve (4 lug.) | 20/08/2026 | 14:00 às 17:00 | Visita externa |

O comando `python manage.py popular_banco` cadastra exatamente essas 4 reservas e os 10 veículos da frota do Porto do Itaqui.
