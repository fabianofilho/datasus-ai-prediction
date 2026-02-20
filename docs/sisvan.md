> [!PRIMARY]
> **SISVAN - Sistema de Vigilância Alimentar e Nutricional**
> O SISVAN é uma ferramenta essencial para a predição de desfechos relacionados ao estado nutricional, especialmente em populações vulneráveis. Ele permite identificar indivíduos em risco de desnutrição, sobrepeso/obesidade e outras carências nutricionais, fornecendo dados para modelos preditivos de saúde metabólica e desenvolvimento infantil.

# Análise do SISVAN para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Vigilância Alimentar e Nutricional (SISVAN) tem como objetivo monitorar o estado nutricional da população brasileira atendida na Atenção Primária à Saúde, com foco especial em crianças, gestantes e beneficiários do Programa Bolsa Família. Ele coleta dados antropométricos (peso, altura, IMC) e informações sobre o consumo alimentar, permitindo a identificação de riscos nutricionais e o planejamento de ações de saúde e nutrição.

## 2. Potencial para Predição com Machine Learning

O SISVAN é uma fonte de dados valiosa para a predição de desfechos relacionados à nutrição e saúde metabólica:

*   **Risco de Desnutrição/Baixo Peso**: Prever a probabilidade de crianças desenvolverem desnutrição ou baixo peso para a idade/altura, com base em seu histórico de crescimento e condições socioeconômicas.
*   **Risco de Sobrepeso/Obesidade**: Modelar a probabilidade de crianças, adolescentes ou adultos desenvolverem sobrepeso ou obesidade, utilizando dados antropométricos longitudinais e informações sobre hábitos alimentares.
*   **Complicações Gestacionais Relacionadas à Nutrição**: Prever o risco de gestantes desenvolverem diabetes gestacional ou hipertensão gestacional, com base em seu estado nutricional pré-gestacional e ganho de peso durante a gravidez.
*   **Impacto do Estado Nutricional em Outros Desfechos**: Utilizando linkage com outras bases, analisar como o estado nutricional influencia o risco de doenças crônicas, internações ou mortalidade.

## 3. Estrutura e Variáveis para Features

O SISVAN registra medições antropométricas e informações sobre o consumo alimentar.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Identificação** | `CNS`, `NIS`, `CPF`, `DT_NASC` | Identificadores, demografia |
| **Antropometria** | `PESO`, `ALTURA`, `IMC` | **Preditores primários** do estado nutricional, séries temporais |
| **Público-alvo** | `TIPO_INDIVIDUO` (Criança, Gestante, Adulto, Idoso) | Segmentação da população |
| **Consumo Alimentar** | `CONSUMO_ALIMENTAR` (variáveis sobre frequência de consumo de alimentos) | Hábitos alimentares, qualidade da dieta |
| **Acompanhamento** | `DT_ACOMPANHAMENTO` | Frequência de monitoramento |

## 4. Identificadores e Record Linkage

O SISVAN possui identificadores que permitem o linkage com outras bases.

*   **Identificadores Disponíveis**: O **CNS** e o **NIS (Número de Identificação Social)** são os principais identificadores. O CPF e a data de nascimento também são importantes para o linkage probabilístico.
*   **Necessidade de Record Linkage**:
    *   **SISVAN - e-SUS AB**: Para integrar o monitoramento nutricional com o acompanhamento de saúde na atenção primária, permitindo uma visão mais completa do paciente.
    *   **SISVAN - SINASC**: Para vincular o estado nutricional da gestante com os desfechos do recém-nascido (ex: baixo peso ao nascer).
    *   **SISVAN - HIPERDIA**: Para analisar a relação entre o estado nutricional e o controle de hipertensão e diabetes.

## 5. Construção de Janelas de Cohort

O SISVAN é adequado para a construção de cohorts de acompanhamento nutricional.

*   **Exemplo (Predição de Obesidade Infantil em 2 anos)**:
    *   **Coorte**: Crianças de 2 a 5 anos com peso adequado para a idade no início da observação.
    *   **Observation Window**: Um período de 12 meses de acompanhamento no SISVAN. Features incluem o IMC inicial, a curva de crescimento, e informações sobre o consumo alimentar.
    *   **Prediction Window**: Os 24 meses seguintes ao final da janela de observação.
    *   **Outcome**: A criança foi classificada com sobrepeso ou obesidade (com base no IMC para idade/sexo) em algum momento dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Qualidade do Preenchimento**: A qualidade e a completude dos dados podem variar, especialmente para as informações sobre consumo alimentar, que dependem da auto-declaração.
*   **Adesão ao Acompanhamento**: O SISVAN depende da adesão dos indivíduos ao acompanhamento na APS, o que pode levar a dados esparsos para alguns pacientes.
*   **Foco em Populações Específicas**: Embora abranja a população atendida na APS, o foco principal em crianças, gestantes e beneficiários do Bolsa Família pode limitar a representatividade para outras faixas etárias ou grupos sociais.

## 7. Referências

1.  Ministério da Saúde (BR), Departamento de Informática do SUS. Sistema de Vigilância Alimentar e Nutricional (SISVAN). Disponível em: [https://datasus.saude.gov.br/acesso-a-informacao/estado-nutricional-sisvan/](https://datasus.saude.gov.br/acesso-a-informacao/estado-nutricional-sisvan/)
2.  Ministério da Saúde (BR). Orientações para a coleta de dados do Sistema de Vigilância Alimentar e Nutricional (SISVAN) na Atenção Básica. Brasília, DF: Ministério da Saúde, 2014.
