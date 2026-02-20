> [!PRIMARY]
> **SIA - Sistema de Informações Ambulatoriais**
> O SIA é crucial para rastrear o cuidado contínuo e o manejo de doenças crônicas fora do ambiente hospitalar. Através do subsistema APAC, ele permite a construção de cohorts longitudinais para pacientes em tratamentos de alto custo, como oncologia e terapia renal substitutiva, tornando-se uma fonte poderosa para prever a resposta ao tratamento, a adesão e a progressão da doença.

# Análise do SIA para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Informações Ambulatoriais (SIA) processa a produção de serviços ambulatoriais (não hospitalares) realizados no âmbito do SUS. Ele é composto por dois principais instrumentos de coleta:

1.  **Boletim de Produção Ambulatorial (BPA)**: Registra procedimentos de baixa e média complexidade. Pode ser consolidado (BPA-C), com dados agregados por procedimento e sem identificação do paciente, ou individualizado (BPA-I), com identificação do paciente.
2.  **Autorização de Procedimentos de Alta Complexidade (APAC)**: É o subsistema mais relevante para a modelagem preditiva. A APAC registra procedimentos de alto custo/complexidade, como quimioterapia, radioterapia, hemodiálise e a dispensação de medicamentos especializados. Cada APAC é nominal e vinculada a um paciente.

## 2. Potencial para Predição com Machine Learning

O potencial do SIA, especialmente da APAC, para machine learning é imenso, focando no acompanhamento de doenças crônicas:

*   **Resposta ao Tratamento Oncológico**: Prever a probabilidade de um paciente com câncer necessitar de uma mudança na linha de tratamento quimioterápico, indicando falha terapêutica.
*   **Adesão à Terapia (Medicamentos de Alto Custo)**: Modelar o risco de um paciente não retirar um medicamento de uso contínuo, permitindo intervenções para melhorar a adesão.
*   **Progressão para Terapia Renal Substitutiva (TRS)**: Em pacientes com doença renal crônica, prever a probabilidade de necessitar de hemodiálise nos próximos meses/anos.
*   **Hospitalização por Complicações**: Utilizando o linkage SIA-SIH, prever o risco de um paciente em tratamento ambulatorial para uma condição crônica (ex: insuficiência cardíaca, DPOC) ser hospitalizado.
*   **Identificação de Pacientes de Alto Custo**: Modelar quais pacientes têm maior probabilidade de se tornarem utilizadores de alto custo dos serviços ambulatoriais.

## 3. Estrutura e Variáveis para Features

As variáveis mais importantes para predição estão no componente APAC do SIA.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Identificação** | `APAC_N_APAC`, `APAC_D_INIC`, `APAC_D_FIM` | Chave da autorização, início e fim da validade |
| **Paciente** | `APAC_N_CNS` (CNS do Paciente), `APAC_N_IDADE`, `APAC_C_SEXO` | **Identificador principal**, demografia |
| **Diagnóstico** | `APAC_C_CIDPRI` (CID-10 Principal) | Condição de base para o tratamento |
| **Procedimento** | `APAC_C_PROCED` (Procedimento Principal) | Tipo de tratamento (ex: quimioterapia, diálise) |
| **Histórico** | `APAC_N_APCAN` (APAC Anterior) | Chave para o encadeamento longitudinal |
| **Medicamentos** | Campos específicos para medicamentos de alto custo | Features sobre o esquema terapêutico |

## 4. Identificadores e Record Linkage

O subsistema APAC é um dos mais bem estruturados do DataSUS em termos de identificação longitudinal.

*   **Identificadores Disponíveis**: O **Cartão Nacional de Saúde (CNS)** é o principal identificador na APAC e tem um bom preenchimento. O campo `APAC_N_APCAN` (Número da APAC Anterior) permite o encadeamento determinístico das autorizações para um mesmo tratamento, criando uma linha do tempo do cuidado do paciente.
*   **Necessidade de Record Linkage**:
    *   **SIA-SIH**: Essencial para avaliar falhas no tratamento ambulatorial que resultam em hospitalização.
    *   **SIA-SIM**: Permite estudos de sobrevida para pacientes em tratamento de doenças crônicas (ex: sobrevida em 5 anos após início da quimioterapia).
    *   **SIA-SINAN**: Conecta o tratamento ambulatorial com a notificação inicial da doença.

## 5. Construção de Janelas de Cohort

A natureza longitudinal da APAC é ideal para a construção de cohorts dinâmicas.

*   **Exemplo (Predição de Mudança de Linha Terapêutica em Câncer de Mama)**:
    *   **Coorte**: Pacientes do sexo feminino com APAC para quimioterapia de câncer de mama (CID-10 C50) iniciando a primeira linha de tratamento.
    *   **Observation Window**: Os primeiros 3 a 6 meses de tratamento. As features podem incluir o tipo de quimioterápico, idade da paciente, e a frequência das APACs.
    *   **Prediction Window**: Os 12 meses seguintes ao final da janela de observação.
    *   **Outcome**: O paciente teve uma nova APAC autorizada para um procedimento que caracteriza a segunda linha de tratamento dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Complexidade do Sistema**: O SIA/APAC possui centenas de códigos de procedimento, e a lógica de quais procedimentos e medicamentos são registrados pode ser complexa e variar ao longo do tempo.
*   **Foco no Procedimento**: O sistema registra o procedimento autorizado e realizado, mas carece de dados clínicos detalhados sobre o estado do paciente (ex: estadiamento do tumor, resultados de exames laboratoriais), que muitas vezes precisam ser inferidos ou buscados em outras fontes.
*   **Fragmentação do Cuidado**: Um paciente pode receber diferentes tipos de cuidado ambulatorial registrados em diferentes partes do SIA (BPA-I, APAC), exigindo um esforço de integração.
*   **BPA-C**: O Boletim de Produção Ambulatorial Consolidado (BPA-C) tem utilidade limitada para modelagem preditiva a nível de paciente, pois os dados são agregados.

## 7. Referências

1.  Britto, C. F., et al. (2023). Mortalidade por doença falciforme a partir de atendimentos ambulatoriais: uma análise comparativa de machine learning. *Hematology, Transfusion and Cell Therapy*, 45, S195.
2.  Ministério da Saúde (BR), Departamento de Informática do SUS. Sistema de Informações Ambulatoriais (SIA/SUS). Disponível em: [https://datasus.saude.gov.br/sistemas-e-aplicativos/ambulatoriais/sia-sus/](https://datasus.saude.gov.br/sistemas-e-aplicativos/ambulatoriais/sia-sus/)
