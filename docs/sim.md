> [!PRIMARY]
> **SIM - Sistema de Informações sobre Mortalidade**
> O SIM é a fonte de dados definitiva para a predição de mortalidade. Ao ser pareado com outras bases de dados (como SIH, SINASC ou SIA), ele se torna a variável-alvo (outcome) para uma vasta gama de modelos de risco, permitindo a análise de sobrevida e a identificação de fatores associados ao óbito.

# Análise do SIM para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Informações sobre Mortalidade (SIM), criado em 1975, é um dos sistemas de informação em saúde mais antigos e consolidados do Brasil. Ele coleta, processa e dissemina dados de todas as Declarações de Óbito (DO) emitidas no país. O SIM é fundamental para a vigilância epidemiológica, a análise da situação de saúde da população e a avaliação do impacto de políticas públicas.

## 2. Potencial para Predição com Machine Learning

O SIM raramente é usado como fonte de *features* para predição, mas é a **fonte primária para a variável-alvo (outcome)** em modelos que visam prever mortalidade. Seu principal uso em machine learning é através do *record linkage* com outras bases de dados, permitindo a construção de cohorts para responder a perguntas como:

*   **Mortalidade após Internação**: Qual o risco de um paciente vir a óbito em 30, 90 ou 365 dias após uma alta hospitalar? (Linkage SIH-SIM)
*   **Mortalidade Neonatal e Infantil**: Quais fatores durante a gestação e o parto estão associados ao óbito no primeiro ano de vida? (Linkage SINASC-SIM)
*   **Sobrevida após Diagnóstico**: Qual a sobrevida esperada de um paciente após o início do tratamento para uma doença crônica, como câncer ou HIV? (Linkage SIA/APAC ou SINAN-SIM)
*   **Mortalidade por Causas Externas**: Quais fatores demográficos e socioeconômicos estão associados a um maior risco de óbito por violência ou acidentes?

## 3. Estrutura e Variáveis Relevantes

As variáveis do SIM são cruciais para definir o desfecho e para análises de subgrupos.

| Categoria | Variáveis Principais | Potencial como Outcome/Feature | 
| :--- | :--- | :--- | 
| **Identificação** | `NUMERODO` (Número da DO) | Chave primária | 
| **Paciente** | `DTNASC`, `IDADE`, `SEXO`, `RACACOR` | Demografia para análise de subgrupos | 
| **Óbito** | `DTOBITO`, `HORAOBITO`, `CAUSABAS` (CID-10) | **Variável-alvo principal (data e causa)** | 
| **Causas** | `LINHAA`, `LINHAB`, `LINHAC`, `LINHAD` | Detalhamento da cascata de eventos que levaram ao óbito | 
| **Local** | `LOCOCOR`, `CODMUNOCOR` | Local de ocorrência do óbito | 
| **Gestacional** | `GESTACAO`, `GRAVIDEZ`, `PARTO`, `PUERPERIO` | Relevante para mortalidade materna e infantil | 

## 4. Identificadores e Record Linkage

Assim como outras bases do DataSUS, o SIM depende de identificadores não únicos para o *record linkage*.

*   **Identificadores Disponíveis**: Os campos mais importantes para o pareamento são `NOME`, `NOMEMAE`, `DTNASC`, `SEXO` e o endereço. O **CNS** e o **CPF** têm sido progressivamente incorporados, melhorando significativamente a qualidade do linkage determinístico e probabilístico.
*   **Necessidade de Record Linkage**: O linkage é **essencial** para o uso do SIM em modelagem preditiva. O processo consiste em pegar uma coorte de pacientes de uma base de origem (ex: todos os pacientes com alta hospitalar do SIH em 2022) e procurar por seus registros na base do SIM nos anos subsequentes para verificar a ocorrência e a data do óbito.

## 5. Construção de Janelas de Cohort

O SIM define o ponto final (ou a censura) na análise de sobrevida.

*   **Exemplo (Mortalidade em 1 ano após diagnóstico de Câncer - Linkage SIA/APAC-SIM)**:
    *   **Index Event**: Primeira APAC de quimioterapia para um paciente com diagnóstico de neoplasia (CID-10 C00-D48) em uma data específica (T0).
    *   **Observation Window**: Pode ser definida como os 6 meses de dados do SIA/APAC *antes* do T0 para coletar features sobre comorbidades e tratamentos prévios.
    *   **Prediction Window**: O período de 1 ano (ou mais) após o T0.
    *   **Outcome**: 
        1.  **Status**: O paciente foi encontrado no SIM dentro da *prediction window*? (1 para óbito, 0 para censura).
        2.  **Tempo**: Se ocorreu óbito, o tempo até o evento é `DTOBITO - T0`. Se não, o tempo de acompanhamento é o final da janela de predição.

## 6. Limitações e Considerações

*   **Qualidade da Causa Básica**: A determinação da causa básica do óbito pode ser imprecisa, especialmente em pacientes idosos com múltiplas comorbidades. O uso de algoritmos para reclassificação de *garbage codes* (causas mal definidas) pode ser necessário.
*   **Atraso na Disponibilização**: Os dados do SIM de um determinado ano são consolidados e disponibilizados no ano seguinte, o que gera um atraso natural na análise.
*   **Sub-registro de Óbitos**: Embora a cobertura do SIM seja considerada alta no Brasil (acima de 95%), pode haver sub-registro em áreas remotas ou de difícil acesso, principalmente em anos mais antigos.
*   **Qualidade dos Identificadores**: A qualidade do preenchimento de nome, nome da mãe e data de nascimento é crucial para o sucesso do *record linkage*. Erros de digitação e dados faltantes são desafios comuns.

## 7. Referências

1.  Morsoleto, R., et al. (2025). Prediction of Infant Mortality in Brazil using Machine Learning and Entity Matching on Brazilian Unified Health System’s Data. *Proceedings of the 13th Symposium on Knowledge Discovery, Mining and Learning*.
2.  Beluzo, C. E., et al. (2020). Machine Learning to Predict Neonatal Mortality Using Public Health Data from São Paulo - Brazil. *medRxiv*.
3.  Ministério da Saúde (BR), Departamento de Informática do SUS. Sistema de Informações sobre Mortalidade (SIM). Disponível em: [https://datasus.saude.gov.br/sistemas-e-aplicativos/epidemiologicos/sim/](https://datasus.saude.gov.br/sistemas-e-aplicativos/epidemiologicos/sim/)
