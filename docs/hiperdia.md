> [!PRIMARY]
> **HIPERDIA - Sistema de Cadastramento e Acompanhamento de Hipertensos e Diabéticos**
> O HIPERDIA é uma ferramenta valiosa para a predição de desfechos em pacientes com hipertensão e diabetes, permitindo o acompanhamento longitudinal e a identificação de fatores de risco para complicações. Embora tenha sido substituído pelo e-SUS AB, seus dados históricos ainda são relevantes para estudos de coorte.

# Análise do HIPERDIA para Modelagem Preditiva com IA

## 1. Descrição Geral

O HIPERDIA foi um sistema de cadastramento e acompanhamento de pacientes hipertensos e diabéticos atendidos na rede ambulatorial do SUS. Seu objetivo era monitorar a saúde desses pacientes, promover o controle das doenças e prevenir complicações. Embora tenha sido gradualmente substituído pelo e-SUS AB, que oferece uma abordagem mais abrangente para a Atenção Primária, os dados históricos do HIPERDIA ainda representam uma fonte de informação importante para estudos de longo prazo.

## 2. Potencial para Predição com Machine Learning

Os dados do HIPERDIA, especialmente quando combinados com outras bases, podem ser utilizados para prever uma série de desfechos relacionados à hipertensão e diabetes:

*   **Complicações Cardiovasculares**: Prever o risco de eventos como infarto agudo do miocárdio (IAM), acidente vascular cerebral (AVC) ou insuficiência cardíaca em pacientes hipertensos e/ou diabéticos.
*   **Progressão da Doença Renal Crônica**: Modelar a probabilidade de um paciente diabético ou hipertenso desenvolver doença renal crônica ou necessitar de terapia renal substitutiva (diálise).
*   **Amputações e Retinopatia Diabética**: Prever o risco de complicações específicas do diabetes, como amputações de membros inferiores ou retinopatia.
*   **Mortalidade**: Identificar pacientes com maior risco de óbito devido a complicações das doenças ou outras causas (requer linkage com o SIM).

## 3. Estrutura e Variáveis para Features

O HIPERDIA registra informações demográficas, clínicas e de acompanhamento dos pacientes.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Identificação** | `CNS`, `CPF`, `NOME`, `DT_NASC` | Identificadores, demografia |
| **Diagnóstico** | `DIAG_HIPERTENSAO`, `DIAG_DIABETES` | Confirmação do diagnóstico |
| **Medições** | `PA_SISTOLICA`, `PA_DIASTOLICA`, `GLICEMIA`, `PESO`, `ALTURA` | Medições clínicas, séries temporais |
| **Comorbidades** | `HAS_COMPLICACOES`, `DM_COMPLICACOES` | Histórico de complicações |
| **Tratamento** | `USO_MEDICAMENTO_HAS`, `USO_MEDICAMENTO_DM` | Adesão ao tratamento medicamentoso |
| **Acompanhamento** | `DT_ULT_CONSULTA`, `DT_PROX_CONSULTA` | Frequência de acompanhamento |

## 4. Identificadores e Record Linkage

O HIPERDIA possui identificadores que facilitam o linkage.

*   **Identificadores Disponíveis**: O **CNS** e o **CPF** são os principais identificadores. Nome completo, data de nascimento e nome da mãe também estão presentes, permitindo o linkage probabilístico.
*   **Necessidade de Record Linkage**:
    *   **HIPERDIA - SIH**: Para verificar internações hospitalares relacionadas a complicações da hipertensão e diabetes.
    *   **HIPERDIA - SIM**: Essencial para analisar a mortalidade e a sobrevida dos pacientes.
    *   **HIPERDIA - SIA/APAC**: Para acompanhar procedimentos ambulatoriais de alto custo (ex: diálise) ou dispensação de medicamentos especializados.
    *   **HIPERDIA - e-SUS AB**: Para complementar o histórico de acompanhamento na atenção primária, especialmente para pacientes que migraram para o novo sistema.

## 5. Construção de Janelas de Cohort

O HIPERDIA permite a construção de cohorts de pacientes com doenças crônicas.

*   **Exemplo (Predição de IAM em 5 anos para pacientes hipertensos)**:
    *   **Coorte**: Pacientes cadastrados no HIPERDIA com diagnóstico de hipertensão, sem histórico de IAM.
    *   **Observation Window**: Um período de 2-3 anos de acompanhamento no HIPERDIA. Features incluem médias de pressão arterial, IMC, uso de medicamentos, e ocorrência de outras comorbidades.
    *   **Prediction Window**: Os 5 anos seguintes ao final da janela de observação.
    *   **Outcome**: O paciente teve um registro de IAM (CID-10 I21) no SIH ou SIM dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Substituição pelo e-SUS AB**: O HIPERDIA não é mais o sistema primário de registro para novos casos, o que significa que a base de dados é estática e não reflete a situação atual da população acompanhada na APS.
*   **Qualidade do Preenchimento**: A qualidade e a completude dos dados podem variar, especialmente para campos de acompanhamento e complicações.
*   **Foco Limitado**: O sistema é focado apenas em hipertensão e diabetes, não capturando outras condições de saúde relevantes para o paciente.

## 7. Referências

1.  Ministério da Saúde (BR), Departamento de Informática do SUS. Hipertensão e Diabetes (HIPERDIA). Disponível em: [https://datasus.saude.gov.br/acesso-a-informacao/hipertensao-e-diabetes-hiperdia/](https://datasus.saude.gov.br/acesso-a-informacao/hipertensao-e-diabetes-hiperdia/)
