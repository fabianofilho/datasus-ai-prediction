> [!PRIMARY]
> **e-SUS Atenção Primária (e-SUS AB / SISAB)**
> O e-SUS AB é a fonte de dados mais promissora para a construção de uma visão longitudinal e integral da saúde do indivíduo na Atenção Primária. Seu potencial para predição reside na capacidade de modelar a transição de um estado de saúde para o desenvolvimento de doenças crônicas, a adesão a cuidados preventivos e o risco de hospitalizações futuras com base em um rico histórico de atendimentos.

# Análise do e-SUS AB / SISAB para Modelagem Preditiva com IA

## 1. Descrição Geral

A estratégia e-SUS Atenção Primária (e-SUS AB) foi criada para reestruturar a coleta de dados na Atenção Primária à Saúde (APS), substituindo o antigo SIAB (Sistema de Informação da Atenção Básica). Os dados coletados através dos sistemas do e-SUS AB (seja o Prontuário Eletrônico do Cidadão - PEC, ou a Coleta de Dados Simplificada - CDS) são centralizados nacionalmente no **Sistema de Informação em Saúde para a Atenção Básica (SISAB)**.

O SISAB, portanto, consolida informações de cadastros individuais e domiciliares, atendimentos, procedimentos, visitas de agentes comunitários de saúde, e condições de saúde da população acompanhada pelas equipes de Saúde da Família.

## 2. Potencial para Predição com Machine Learning

O e-SUS AB/SISAB é ideal para modelos preditivos focados na prevenção e no manejo de condições crônicas em nível comunitário:

*   **Risco de Desenvolvimento de Doenças Crônicas**: Prever a probabilidade de um indivíduo desenvolver hipertensão ou diabetes nos próximos anos, com base em seu histórico de medições (pressão arterial, glicemia), dados antropométricos e estilo de vida.
*   **Risco de Hospitalização por Condições Sensíveis à Atenção Primária (ICSAP)**: Identificar pacientes com doenças crônicas (ex: asma, insuficiência cardíaca) com alto risco de serem hospitalizados, permitindo um manejo mais intensivo na APS.
*   **Baixa Adesão a Programas Preventivos**: Modelar o risco de uma gestante não comparecer ao número adequado de consultas de pré-natal ou de um paciente com hipertensão não aderir ao acompanhamento.
*   **Predição de Agudização de Doenças Crônicas**: Prever a probabilidade de um paciente diabético apresentar um pico de descompensação glicêmica.

## 3. Estrutura e Variáveis para Features

O SISAB possui uma estrutura de dados granular, registrando cada interação do paciente com a equipe de saúde.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Cadastro** | `co_seq_fat_cad_individual`, `co_cns`, `dt_nascimento`, `co_dim_sexo` | Identificador, demografia |
| **Condições** | `co_fat_cidadao_pec` (Problema/Condição Avaliada) | Comorbidades, histórico de saúde |
| **Medições** | `nu_pa_sistolica`, `nu_pa_diastolica`, `nu_glicemia`, `nu_peso`, `nu_altura` | **Preditores clínicos primários**, séries temporais |
| **Atendimentos** | `co_seq_fat_atd_ind`, `dt_atendimento` | Frequência de uso do serviço |
| **Procedimentos** | `co_procedimento` | Ações de saúde realizadas |

## 4. Identificadores e Record Linkage

O e-SUS AB é um dos sistemas mais bem preparados para a identificação do paciente.

*   **Identificadores Disponíveis**: O **CNS** é o identificador central do sistema. O **CPF** também é amplamente utilizado. Isso facilita enormemente tanto o acompanhamento longitudinal do paciente dentro do próprio sistema quanto o linkage com outras bases.
*   **Necessidade de Record Linkage**:
    *   **SISAB-SIH**: Crucial para validar modelos que preveem hospitalizações. Permite verificar se os pacientes identificados como de alto risco na APS de fato internaram.
    *   **SISAB-SIM**: Permite analisar a mortalidade e como o acompanhamento na APS impacta a sobrevida.
    *   **SISAB-SIA**: Conecta o cuidado na APS com tratamentos de média e alta complexidade.

## 5. Construção de Janelas de Cohort

A natureza de série temporal dos dados do SISAB é perfeita para a construção de janelas de observação dinâmicas.

*   **Exemplo (Predição de Risco de Hipertensão em 2 anos)**:
    *   **Coorte**: Indivíduos cadastrados na APS, com idade entre 30-50 anos, sem diagnóstico prévio de hipertensão.
    *   **Observation Window**: Um período de 12 meses de dados. As features seriam séries temporais das medições de pressão arterial, evolução do IMC (calculado a partir de peso e altura), e frequência de consultas.
    *   **Prediction Window**: Os 24 meses seguintes ao final da janela de observação.
    *   **Outcome**: O paciente recebeu um diagnóstico de hipertensão (registrado como "Problema/Condição Avaliada") ou iniciou o uso de anti-hipertensivos (verificado via linkage com SIA) dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Adoção e Qualidade**: A qualidade dos dados do SISAB depende da implantação do prontuário eletrônico nos municípios. A cobertura e a qualidade do preenchimento ainda não são uniformes em todo o Brasil.
*   **Dados Não Estruturados**: Uma parte significativa da informação clínica no prontuário eletrônico está em campos de texto livre (evolução, anamnese), cujo uso para modelagem exige técnicas de Processamento de Linguagem Natural (PLN).
*   **Volume de Dados**: O SISAB gera um volume massivo de dados, o que pode exigir uma infraestrutura de Big Data para processamento e análise.
*   **Variabilidade na Coleta**: A frequência e o padrão de registro de informações (como aferição de pressão) podem variar entre diferentes equipes e municípios, o que pode introduzir vieses.

## 7. Referências

1.  Ministério da Saúde (BR). Estratégia e-SUS Atenção Primária. Disponível em: [https://sisab.saude.gov.br/](https://sisab.saude.gov.br/)
2.  Maciel, F. B. M., et al. (2022). Implantação da Estratégia e-SUS Atenção Básica no Brasil: análise de dados de 2014 a 2019. *Revista de Saúde Pública*, 56, 5.
