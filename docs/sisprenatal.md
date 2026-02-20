> [!PRIMARY]
> **SIS-Pré-Natal (SISPRENATAL)**
> O SISPRENATAL é uma ferramenta crucial para a predição de desfechos maternos e neonatais, focando no acompanhamento da gestação. Ele permite identificar gestantes de risco, avaliar a qualidade do pré-natal e prever complicações como parto prematuro, pré-eclâmpsia e mortalidade materna e infantil.

# Análise do SIS-Pré-Natal (SISPRENATAL) para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Informação do Pré-Natal (SISPRENATAL) foi um sistema desenvolvido para registrar e acompanhar as gestantes e os cuidados de pré-natal recebidos no SUS. Seu objetivo era monitorar a qualidade da assistência pré-natal, identificar gestantes de risco e garantir o acesso a exames e procedimentos necessários. Embora tenha sido substituído por módulos de pré-natal dentro do e-SUS AB, seus dados históricos continuam sendo uma fonte valiosa para estudos de coorte sobre a saúde materno-infantil.

## 2. Potencial para Predição com Machine Learning

Os dados do SISPRENATAL, especialmente quando combinados com outras bases, são fundamentais para prever desfechos importantes na gestação e no período neonatal:

*   **Parto Prematuro**: Prever a probabilidade de um parto ocorrer antes de 37 semanas de gestação, com base em fatores de risco maternos e no histórico do pré-natal.
*   **Pré-eclâmpsia/Eclâmpsia**: Modelar o risco de gestantes desenvolverem síndromes hipertensivas da gravidez, utilizando medições de pressão arterial, exames laboratoriais e histórico clínico.
*   **Diabetes Gestacional**: Identificar gestantes com maior risco de desenvolver diabetes gestacional, com base em fatores demográficos, histórico familiar e resultados de exames.
*   **Baixo Peso ao Nascer**: Prever a probabilidade de o recém-nascido apresentar baixo peso, correlacionando com a qualidade do pré-natal e condições maternas.
*   **Mortalidade Materna e Neonatal**: Quando pareado com o SIM e o SINASC, o SISPRENATAL permite identificar fatores de risco durante a gestação associados ao óbito materno ou neonatal.

## 3. Estrutura e Variáveis para Features

O SISPRENATAL registra informações detalhadas sobre a gestante e o acompanhamento pré-natal.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Identificação** | `CNS_GESTA`, `CPF_GESTA`, `NOME_GESTA`, `DT_NASC_GESTA` | Identificadores, demografia da gestante |
| **Gestação** | `DT_DUM` (Data da Última Menstruação), `IG_INICIAL` (Idade Gestacional Inicial) | Cálculo da idade gestacional, data provável do parto |
| **Pré-natal** | `NUM_CONSULTAS`, `DT_PRIMEIRA_CONSULTA`, `DT_ULTIMA_CONSULTA` | Frequência e início do pré-natal |
| **Exames** | `RESULT_SORO_HIV`, `RESULT_VDRL`, `RESULT_GLICEMIA` | Resultados de exames importantes |
| **Condições** | `HAS_GESTA`, `DM_GESTA`, `TABAGISMO`, `ALCOOLISMO` | Comorbidades e hábitos de risco |
| **Desfecho** | `TIPO_PARTO`, `DT_PARTO`, `PESO_RN` | Desfechos do parto e do recém-nascido (para linkage) |

## 4. Identificadores e Record Linkage

O SISPRENATAL possui identificadores que facilitam o linkage.

*   **Identificadores Disponíveis**: O **CNS** e o **CPF** da gestante são os principais identificadores. Nome completo, data de nascimento e nome da mãe também são cruciais para o linkage probabilístico.
*   **Necessidade de Record Linkage**:
    *   **SISPRENATAL - SINASC**: Essencial para vincular o acompanhamento pré-natal com os dados do nascimento e do recém-nascido, permitindo avaliar o impacto do pré-natal nos desfechos neonatais.
    *   **SISPRENATAL - SIM**: Para identificar casos de mortalidade materna e neonatal, correlacionando com a qualidade do pré-natal.
    *   **SISPRENATAL - SIH**: Para verificar internações hospitalares da gestante durante a gravidez ou do recém-nascido após o parto.
    *   **SISPRENATAL - e-SUS AB**: Para complementar o histórico de acompanhamento na atenção primária, especialmente para gestantes que migraram para o novo sistema.

## 5. Construção de Janelas de Cohort

O SISPRENATAL é ideal para a construção de cohorts de gestantes.

*   **Exemplo (Predição de Parto Prematuro)**:
    *   **Coorte**: Todas as gestantes cadastradas no SISPRENATAL.
    *   **Observation Window**: O período do pré-natal até a 28ª semana de gestação. Features incluem idade da gestante, número de consultas, histórico de partos prematuros, resultados de exames e comorbidades.
    *   **Prediction Window**: Da 28ª semana de gestação até a data provável do parto.
    *   **Outcome**: O parto ocorreu antes de 37 semanas de gestação (verificado via linkage com SINASC) dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Substituição pelo e-SUS AB**: O SISPRENATAL não é mais o sistema primário de registro para novos casos, o que significa que a base de dados é estática e não reflete a situação atual do acompanhamento pré-natal.
*   **Qualidade do Preenchimento**: A qualidade e a completude dos dados podem variar, especialmente para campos de acompanhamento e resultados de exames.
*   **Foco Limitado**: O sistema é focado apenas no pré-natal, não capturando o histórico de saúde completo da mulher antes da gestação ou após o puerpério, a menos que seja feito linkage com outras bases.

## 7. Referências

1.  Ministério da Saúde (BR). Manual Técnico do SISPRENATAL. Disponível em: [https://bvsms.saude.gov.br/bvs/publicacoes/manual_sisprenatal.pdf](https://bvsms.saude.gov.br/bvs/publicacoes/manual_sisprenatal.pdf)
2.  Ministério da Saúde (BR). Atenção ao Pré-Natal de Baixo Risco. Cadernos de Atenção Básica, n. 32. Brasília, DF: Ministério da Saúde, 2012.
