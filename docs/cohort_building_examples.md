> [!NOTE]
> A construção de cohorts é uma etapa fundamental na modelagem preditiva em saúde. Ela envolve a definição clara de uma população de estudo, um evento índice, janelas de observação e predição, e o desfecho de interesse. Este documento apresenta exemplos práticos de como essas cohorts podem ser estruturadas utilizando os dados do DataSUS.

# Exemplos de Construção de Cohorts para Predição com DataSUS

## 1. Conceitos Fundamentais

Antes de mergulharmos nos exemplos, é crucial entender os conceitos-chave:

*   **População de Estudo**: O grupo de indivíduos que será incluído na análise. Deve ser definida com base nos critérios de inclusão e exclusão.
*   **Evento Índice (Index Event)**: O ponto de partida para a observação de cada indivíduo na coorte. Pode ser uma internação, um diagnóstico, um nascimento, etc.
*   **Janela de Observação (Observation Window)**: O período *antes* do evento índice (ou no momento dele) durante o qual as variáveis (features) são coletadas. Quanto mais longa, mais rica em informações, mas também mais suscetível a dados faltantes.
*   **Janela de Predição (Prediction Window)**: O período *após* o evento índice (ou após a janela de observação) no qual o desfecho de interesse é verificado. A duração depende do desfecho (ex: 30 dias para reinternação, 5 anos para mortalidade).
*   **Desfecho (Outcome)**: A variável que se deseja prever (ex: óbito, reinternação, desenvolvimento de doença). Deve ser claramente definida como binária (sim/não) ou temporal (tempo até o evento).

## 2. Exemplo 1: Predição de Reinternação Hospitalar em 30 Dias (SIH)

**Objetivo**: Prever quais pacientes terão uma nova internação hospitalar em até 30 dias após a alta de uma internação índice.

*   **População de Estudo**: Todos os pacientes adultos (idade > 18 anos) que tiveram uma internação no SIH com alta (motivo de saída = alta) em um determinado período (ex: 2018-2022).
*   **Evento Índice**: A data de alta (`DT_SAIDA`) da internação. Cada alta é um evento índice potencial.
*   **Janela de Observação**: A própria internação que resultou na alta. As features seriam extraídas das variáveis da AIH (diagnóstico principal, procedimentos realizados, idade, sexo, tempo de permanência, etc.).
*   **Janela de Predição**: Os 30 dias subsequentes à `DT_SAIDA`.
*   **Desfecho (Outcome)**: Ocorrência de uma nova internação (identificada por um novo `N_AIH` para o mesmo paciente, via *record linkage*) dentro da janela de predição. Se sim, `reinternou = 1`; se não, `reinternou = 0`.
*   **Linkage Necessário**: Intra-SIH (para identificar internações subsequentes do mesmo paciente) e, idealmente, com o SIM (para censurar pacientes que foram a óbito antes de poderem ser reinternados).

## 3. Exemplo 2: Predição de Mortalidade Neonatal (SINASC + SIM)

**Objetivo**: Prever quais recém-nascidos terão óbito nos primeiros 28 dias de vida, com base em características do nascimento e da mãe.

*   **População de Estudo**: Todos os nascidos vivos registrados no SINASC em um determinado período (ex: 2019-2023).
*   **Evento Índice**: A data de nascimento (`DTNASC`) do recém-nascido.
*   **Janela de Observação**: O momento do nascimento. As features seriam extraídas das variáveis da Declaração de Nascido Vivo (DN) (peso ao nascer, idade gestacional, Apgar, idade da mãe, número de consultas pré-natal, etc.).
*   **Janela de Predição**: Os 28 dias subsequentes à `DTNASC`.
*   **Desfecho (Outcome)**: Ocorrência de óbito neonatal (identificado por *record linkage* com o SIM, onde `DTOBITO` está dentro da janela de predição e `IDADE` do óbito é < 28 dias). Se sim, `obito_neonatal = 1`; se não, `obito_neonatal = 0`.
*   **Linkage Necessário**: SINASC-SIM (probabilístico, usando nome da mãe, data de nascimento do bebê, etc.).

## 4. Exemplo 3: Predição de Abandono de Tratamento de Tuberculose (SINAN)

**Objetivo**: Prever quais pacientes com tuberculose abandonarão o tratamento, com base em características sociodemográficas e clínicas iniciais.

*   **População de Estudo**: Todos os casos novos de tuberculose pulmonar notificados no SINAN em um determinado período (ex: 2017-2021) que iniciaram tratamento.
*   **Evento Índice**: A data de início do tratamento (`DT_INIC_TRAT`) registrada na ficha de notificação.
*   **Janela de Observação**: O momento da notificação e início do tratamento. Features incluem idade, sexo, raça, escolaridade, forma clínica da doença, baciloscopia inicial, e informações sobre o município de residência (linkage com CNES para características da unidade de saúde).
*   **Janela de Predição**: O período padrão do tratamento (geralmente 6 meses).
*   **Desfecho (Outcome)**: O campo `EVOLUCAO` na ficha de encerramento do caso foi preenchido como "Abandono"? Se sim, `abandono = 1`; se não (cura, óbito, transferência), `abandono = 0`.
*   **Linkage Necessário**: Intra-SINAN (para vincular a notificação inicial com a ficha de encerramento do caso) e, opcionalmente, com o SIM (para identificar óbitos como desfecho competitivo).

## 5. Exemplo 4: Predição de Risco de Hospitalização por ICSAP (e-SUS AB + SIH)

**Objetivo**: Prever quais pacientes acompanhados na Atenção Primária terão uma internação por Condições Sensíveis à Atenção Primária (ICSAP) nos próximos 12 meses.

*   **População de Estudo**: Pacientes adultos cadastrados e acompanhados regularmente no e-SUS AB (SISAB) com diagnóstico de condições crônicas (ex: HAS, DM, asma) em um determinado ano (ex: 2020).
*   **Evento Índice**: A data da última consulta ou atendimento registrado no e-SUS AB dentro da janela de observação.
*   **Janela de Observação**: Os 12 meses anteriores ao evento índice. Features incluem histórico de atendimentos, medições (PA, glicemia, peso), diagnósticos registrados, medicamentos em uso, e dados sociodemográficos do cadastro individual.
*   **Janela de Predição**: Os 12 meses seguintes ao evento índice.
*   **Desfecho (Outcome)**: Ocorrência de internação por ICSAP (identificada por *record linkage* com o SIH, onde o `DIAG_PRINC` da AIH corresponde a uma ICSAP) dentro da janela de predição. Se sim, `internou_icsap = 1`; se não, `internou_icsap = 0`.
*   **Linkage Necessário**: e-SUS AB (SISAB)-SIH (determinístico ou probabilístico, usando CNS/CPF, nome, data de nascimento).

## 6. Referências

1.  Guerra Junior, A. A., et al. (2018). Building the National Database of Health Centred on the Individual: Administrative and Epidemiological Record Linkage - Brazil, 2000-2015. *International Journal of Population Data Science*, 3(1).
2.  Morsoleto, R., et al. (2025). Prediction of Infant Mortality in Brazil using Machine Learning and Entity Matching on Brazilian Unified Health System’s Data. *Proceedings of the 13th Symposium on Knowledge Discovery, Mining and Learning*.
3.  Rodrigues, M. M. S., et al. (2024). Machine learning algorithms using national registry data to predict loss to follow-up during tuberculosis treatment. *BMC Public Health*, 24(1), 1-11.
4.  Maciel, F. B. M., et al. (2022). Implantação da Estratégia e-SUS Atenção Básica no Brasil: análise de dados de 2014 a 2019. *Revista de Saúde Pública*, 56, 5.
