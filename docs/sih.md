> [!PRIMARY]
> **SIH - Sistema de Informações Hospitalares**
> O SIH é um dos sistemas mais importantes para a predição de desfechos clínicos e de gestão em saúde, registrando todas as internações financiadas pelo SUS. Sua natureza longitudinal (para pacientes com múltiplas internações) e a riqueza de detalhes clínicos o tornam uma fonte primária para modelos de risco.

# Análise do SIH para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Informações Hospitalares (SIH) consolida os dados das Autorizações de Internação Hospitalar (AIH), que são os registros de todas as internações realizadas e financiadas pelo Sistema Único de Saúde (SUS) no Brasil. Implementado em 1992, o SIH processa mais de 12 milhões de internações anualmente, contendo um vasto repositório de informações demográficas, administrativas e clínicas sobre os pacientes.

## 2. Potencial para Predição com Machine Learning

O SIH é extremamente valioso para a construção de modelos preditivos, principalmente para os seguintes desfechos:

*   **Reinternação Hospitalar**: Modelar o risco de um paciente ser reinternado em 30, 90 ou 180 dias após a alta. Este é um dos casos de uso mais clássicos e de maior impacto na gestão de leitos e na continuidade do cuidado.
*   **Mortalidade Intra-hospitalar**: Prever o risco de óbito durante a internação, permitindo a identificação de pacientes de alto risco que podem se beneficiar de intervenções precoces.
*   **Tempo de Permanência Prolongado**: Estimar a probabilidade de uma internação exceder um determinado período (ex: 15 dias), auxiliando no planejamento de recursos hospitalares.
*   **Complicações e Eventos Adversos**: Identificar pacientes com maior risco de desenvolver complicações específicas (ex: infecção hospitalar, insuficiência renal aguda) com base nas condições de admissão e procedimentos realizados.
*   **Custos Hospitalares Elevados**: Modelar a probabilidade de uma internação gerar custos acima de um determinado percentil, auxiliando na gestão financeira.

## 3. Estrutura e Variáveis para Features

O SIH é rico em variáveis que podem ser utilizadas como features em modelos de machine learning. As mais relevantes incluem:

| Categoria | Variáveis Principais | Potencial como Feature | 
| :--- | :--- | :--- | 
| **Identificação** | `N_AIH` (Número da AIH), `ANO_CMPT`, `MES_CMPT` | Chaves primárias e temporais | 
| **Paciente** | `SEXO`, `IDADE`, `DT_NASC`, `RACA_COR`, `CEP` | Demografia, base para engenharia de features | 
| **Internação** | `CAR_INT` (Caráter da internação), `DT_INTER`, `DT_SAIDA` | Urgência, cálculo do tempo de permanência | 
| **Diagnóstico** | `DIAG_PRINC` (CID-10), `DIAG_SEC` (CID-10) | Principal preditor clínico, comorbidades | 
| **Procedimento** | `PROC_SOLIC`, `PROC_REA` | Intervenções realizadas, complexidade | 
| **Desfecho** | `MOT_SAIDA` (Motivo da saída/alta) | Variável alvo (óbito, alta, etc.) | 
| **Valores** | `VAL_TOT`, `VAL_UTI`, `DIARIAS`, `UTI_MES_TO` | Proxies de intensidade do cuidado | 
| **UTI** | `UTI_MES_IN`, `UTI_MES_AN`, `UTI_MES_AL`, `UTI_MES_TO` | Indicador de gravidade | 

## 4. Identificadores e Record Linkage

Construir uma visão longitudinal do paciente é fundamental para muitos modelos preditivos, como o de reinternação. O SIH, no entanto, apresenta desafios para o *record linkage*.

*   **Identificadores Disponíveis**: Historicamente, o SIH não possuía um identificador único robusto. O número da AIH é único por internação, não por paciente. O `N_AIH` de uma internação anterior pode ser encontrado no campo `AIH_ANT`, mas isso só se aplica a internações no mesmo hospital. O **Cartão Nacional de Saúde (CNS)** e o **CPF** foram sendo progressivamente adicionados e hoje são os melhores identificadores disponíveis, embora a qualidade e o preenchimento possam variar ao longo do tempo e entre regiões.
*   **Necessidade de Record Linkage**: Para vincular internações de um mesmo paciente em diferentes hospitais ou para conectar o SIH a outras bases (como SIM ou SINASC), o *record linkage* probabilístico é indispensável. As chaves de bloqueio e pareamento geralmente utilizam uma combinação de:
    *   Nome completo do paciente
    *   Data de nascimento
    *   Nome da mãe
    *   Sexo
    *   Município de residência

## 5. Construção de Janelas de Cohort

A criação de janelas de observação e predição é central para a modelagem de desfechos futuros.

*   **Exemplo (Predição de Reinternação em 30 dias)**:
    *   **Index Event**: Uma internação que resultou em alta (`MOT_SAIDA` = alta).
    *   **Observation Window**: O período da internação índice. As variáveis desta internação (`DIAG_PRINC`, `IDADE`, `PROC_REA`, etc.) formam o vetor de features.
    *   **Prediction Window**: Os 30 dias seguintes à data de saída (`DT_SAIDA`).
    *   **Outcome**: Ocorreu uma nova internação para o mesmo paciente dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Qualidade do Preenchimento**: A acurácia dos diagnósticos (principal e secundários) pode variar. O CID-10 secundário, crucial para capturar comorbidades, é frequentemente subnotificado.
*   **Variação Temporal**: Os formulários da AIH e as variáveis disponíveis mudaram ao longo dos anos. Análises longitudinais longas devem considerar essas mudanças.
*   **Foco no Evento**: O SIH registra o evento da internação, não o cuidado contínuo. Informações sobre o estado do paciente antes da admissão ou após a alta são limitadas, a menos que seja feito o *linkage* com outras bases (como SIA ou e-SUS AB).
*   **Representatividade**: O SIH cobre apenas as internações financiadas pelo SUS, excluindo a saúde suplementar (planos de saúde), que representa cerca de 25% da população brasileira.

## 7. Referências

1.  Guerra Junior, A. A., et al. (2018). Building the National Database of Health Centred on the Individual: Administrative and Epidemiological Record Linkage - Brazil, 2000-2015. *International Journal of Population Data Science*, 3(1).
2.  Ali, M. S., et al. (2019). Administrative Data Linkage in Brazil: Potentials for Health Technology Assessment. *Frontiers in Pharmacology*, 10, 984.
3.  Ministério da Saúde (BR), Departamento de Informática do SUS. Sistema de Informações Hospitalares do SUS (SIH/SUS). Disponível em: [https://datasus.saude.gov.br/sistemas-e-aplicativos/hospitalares/sih-sus/](https://datasus.saude.gov.br/sistemas-e-aplicativos/hospitalares/sih-sus/)
