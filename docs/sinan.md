> [!PRIMARY]
> **SINAN - Sistema de Informação de Agravos de Notificação**
> O SINAN é a principal fonte para o estudo e predição de desfechos relacionados a doenças infecciosas e outros agravos de notificação compulsória. Sua estrutura longitudinal (para doenças que exigem acompanhamento) permite modelar a progressão da doença, a resposta ao tratamento e a ocorrência de complicações.

# Análise do SINAN para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Informação de Agravos de Notificação (SINAN) é alimentado pela notificação e investigação de casos de doenças e agravos que constam na lista nacional de notificação compulsória. Isso inclui uma vasta gama de condições, desde doenças infecciosas como tuberculose, HIV/AIDS, dengue e hanseníase, até agravos como violência doméstica e acidentes de trabalho. Cada agravo possui uma ficha de notificação específica com variáveis relevantes para sua vigilância epidemiológica.

## 2. Potencial para Predição com Machine Learning

O potencial do SINAN para machine learning é vasto e específico para cada agravo. Alguns exemplos de desfechos que podem ser preditos são:

*   **Abandono de Tratamento (Tuberculose, Hanseníase)**: Prever a probabilidade de um paciente abandonar o tratamento antes da conclusão, permitindo intervenções de busca ativa e adesão.
*   **Evolução para Óbito (Dengue, COVID-19, HIV/AIDS)**: Identificar pacientes com maior risco de evoluir para formas graves da doença ou para o óbito, com base nos sintomas e condições iniciais.
*   **Desenvolvimento de Resistência a Medicamentos (Tuberculose)**: Modelar o risco de um paciente desenvolver resistência aos fármacos com base em seu histórico de tratamento e características clínicas.
*   **Ocorrência de Surtos (Dengue, Chikungunya)**: Utilizar dados de notificação em conjunto com dados climáticos e geográficos para prever a ocorrência de surtos em determinadas áreas.
*   **Recidiva (Hanseníase, Violência)**: Prever o risco de um paciente apresentar uma recidiva da doença ou de um novo episódio de violência após um evento inicial.

## 3. Estrutura e Variáveis para Features

A estrutura de variáveis do SINAN é modular, com um bloco de informações gerais e blocos específicos para cada agravo.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Notificação** | `ID_AGRAVO`, `DT_NOTIFIC`, `SEM_NOT` | Tipo de doença, data e semana epidemiológica |
| **Paciente** | `DT_NASC`, `NU_IDADE_N`, `CS_SEXO`, `CS_RACA` | Demografia básica |
| **Residência** | `ID_MN_RESI` (Município de Residência) | Informação geográfica crucial para análises espaciais |
| **Dados Clínicos** | Variáveis específicas do agravo (ex: `BACILOSCO`, `TRAT_SUPERV` para Tuberculose; `CLASSI_FIN` para Dengue) | **Principais preditores clínicos** |
| **Evolução** | `EVOLUCAO` (Cura, óbito, abandono) | **Variável-alvo principal** |

## 4. Identificadores e Record Linkage

O SINAN possui desafios de identificação semelhantes a outros sistemas do DataSUS.

*   **Identificadores Disponíveis**: A ficha de notificação contém campos para `NM_PACIENT` (Nome do Paciente), `NM_MAE_PAC` (Nome da Mãe) e `DT_NASC_PAC` (Data de Nascimento). O **CNS** e o **CPF** são cada vez mais utilizados, mas sua presença não é universal, especialmente em notificações mais antigas.
*   **Necessidade de Record Linkage**:
    *   **Intra-base (Longitudinal)**: Para doenças de acompanhamento (ex: Tuberculose, HIV), é necessário vincular a ficha de notificação inicial com as fichas de acompanhamento subsequentes para construir o histórico do paciente.
    *   **SINAN-SIM**: Essencial para confirmar o óbito como desfecho e analisar a mortalidade específica por agravo.
    *   **SINAN-SIH**: Permite estudar as hospitalizações decorrentes de um agravo de notificação.
    *   **SINAN-SIA**: Pode ser usado para acompanhar o uso de medicamentos e outros procedimentos ambulatoriais relacionados ao tratamento do agravo.

## 5. Construção de Janelas de Cohort

A construção de cohorts no SINAN é geralmente orientada pelo agravo.

*   **Exemplo (Predição de Abandono de Tratamento de Tuberculose)**:
    *   **Coorte**: Todos os pacientes com notificação de caso novo de tuberculose em um determinado período.
    *   **Observation Window**: O momento da notificação. As features são as variáveis da ficha de notificação (`NU_IDADE_N`, tipo de tuberculose, `RAIOX_TORA`, etc.).
    *   **Prediction Window**: O período de tratamento padrão (geralmente 6 meses).
    *   **Outcome**: O campo `EVOLUCAO` na ficha de encerramento do caso foi preenchido como "Abandono"? (Sim/Não).

## 6. Limitações e Considerações

*   **Subnotificação**: A notificação de casos depende da suspeita clínica e do registro pelo profissional de saúde, o que pode levar à subnotificação, especialmente para doenças com sintomas leves ou em áreas com acesso limitado à saúde.
*   **Qualidade e Padronização**: A qualidade do preenchimento das fichas pode variar muito. Além disso, as fichas e variáveis podem mudar ao longo do tempo, exigindo harmonização para estudos longitudinais.
*   **Duplicidade de Registros**: Um mesmo paciente pode ser notificado mais de uma vez para o mesmo episódio da doença, exigindo um processo de deduplicação antes da análise.
*   **Dados de Localização**: Embora o município de residência seja bem registrado, dados mais granulares (bairro, endereço) podem ser imprecisos, dificultando análises geoespaciais detalhadas.

## 7. Referências

1.  Rodrigues, M. M. S., et al. (2024). Machine learning algorithms using national registry data to predict loss to follow-up during tuberculosis treatment. *BMC Public Health*, 24(1), 1-11.
2.  Ministério da Saúde (BR). Portaria GM/MS Nº 204, de 17 de fevereiro de 2016. Define a Lista Nacional de Notificação Compulsória de doenças, agravos e eventos de saúde pública.
3.  Ministério da Saúde (BR), Departamento de Informática do SUS. Sistema de Informação de Agravos de Notificação (SINAN). Disponível em: [https://datasus.saude.gov.br/sistemas-e-aplicativos/epidemiologicos/sinan/](https://datasus.saude.gov.br/sistemas-e-aplicativos/epidemiologicos/sinan/)
