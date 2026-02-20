> [!PRIMARY]
> **SINASC - Sistema de Informações sobre Nascidos Vivos**
> O SINASC é a principal fonte de dados para a predição de desfechos neonatais e de saúde materno-infantil. Suas variáveis detalhadas sobre a gestação, o parto e as condições do recém-nascido o tornam ideal para modelos de risco focados no início da vida.

# Análise do SINASC para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Informações sobre Nascidos Vivos (SINASC), implementado em 1990, tem como objetivo coletar e sistematizar os dados de todas as Declarações de Nascido Vivo (DN) emitidas no país. Ele é uma ferramenta essencial para a construção de indicadores de saúde materno-infantil, para a vigilância epidemiológica de anomalias congênitas e para o planejamento de políticas de saúde voltadas para gestantes e recém-nascidos.

## 2. Potencial para Predição com Machine Learning

O SINASC é uma fonte de dados extremamente rica para a predição de uma variedade de desfechos de saúde no início da vida. Os principais casos de uso incluem:

*   **Baixo Peso ao Nascer**: Prever a probabilidade de um recém-nascido ter peso inferior a 2.500 gramas, um importante indicador de risco para a saúde futura.
*   **Prematuridade**: Modelar o risco de um nascimento ocorrer antes de 37 semanas de gestação.
*   **Apgar Baixo no 5º Minuto**: Prever a probabilidade de um recém-nascido apresentar um índice de Apgar < 7 no quinto minuto de vida, um indicador de asfixia perinatal e risco neurológico.
*   **Anomalias Congênitas**: Identificar fatores de risco maternos e gestacionais associados à ocorrência de anomalias congênitas.
*   **Mortalidade Neonatal e Infantil**: Quando pareado com o SIM, o SINASC é a base para a construção de modelos preditivos de óbito neonatal (primeiros 28 dias) e infantil (primeiro ano de vida), permitindo a identificação de gestantes e recém-nascidos de alto risco.

## 3. Estrutura e Variáveis para Features

O SINASC contém um conjunto detalhado de variáveis sobre a mãe, a gestação, o parto e o recém-nascido, que servem como um excelente conjunto de features.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Mãe** | `IDADEMAE`, `ESCMAE` (Escolaridade), `RACACORMAE`, `ESTCIVMAE` | Demografia e background socioeconômico materno |
| **Gestação** | `GESTACAO`, `GRAVIDEZ`, `PARTO`, `CONSULTAS` (Nº de consultas pré-natal) | Duração da gestação, tipo de gravidez, tipo de parto, qualidade do pré-natal |
| **Recém-nascido** | `SEXO`, `PESO`, `APGAR1`, `APGAR5`, `RACACOR` | **Variáveis-alvo** (Peso, Apgar) e features demográficas |
| **Anomalias** | `IDANOMAL` (Presença de anomalia), `CODANOMAL` (CID-10 da anomalia) | Variável-alvo para modelos específicos |
| **Parto** | `TPAPRESENT` (Apresentação fetal), `STTRABPART` (Trabalho de parto induzido) | Detalhes clínicos do parto |

## 4. Identificadores e Record Linkage

O linkage do SINASC com outras bases de dados amplia enormemente seu potencial analítico.

*   **Identificadores Disponíveis**: O principal identificador é o `NUMERODN` (Número da Declaração de Nascido Vivo). Para o linkage, os campos-chave são o nome da mãe (`NOMEMAE`), data de nascimento da mãe, e o nome e data de nascimento do recém-nascido. O **CNS da mãe** e do recém-nascido são os identificadores mais robustos quando disponíveis.
*   **Necessidade de Record Linkage**:
    *   **SINASC-SIM**: Este é o linkage mais importante e clássico. Ele permite identificar quais dos nascidos vivos em um determinado ano vieram a óbito, transformando o SINASC em uma coorte de nascimento para estudos de mortalidade infantil.
    *   **SINASC-SIH**: Permite estudar as internações hospitalares de crianças durante seus primeiros anos de vida, analisando como as condições do nascimento impactam a morbidade futura.
    *   **SINASC-SI-PNI**: Vincula os dados do nascimento com o histórico de vacinação da criança.

## 5. Construção de Janelas de Cohort

O SINASC é a base para a construção de coortes de nascimento.

*   **Exemplo (Predição de Mortalidade Neonatal - Linkage SINASC-SIM)**:
    *   **Coorte**: Todos os nascidos vivos registrados no SINASC em um determinado ano (ex: 2022).
    *   **Observation Window**: Corresponde ao momento do nascimento. As features são todas as variáveis coletadas na DN (`IDADEMAE`, `PESO`, `GESTACAO`, `APGAR1`, etc.).
    *   **Prediction Window**: Os primeiros 28 dias de vida do recém-nascido.
    *   **Outcome**: O recém-nascido foi encontrado no SIM com data do óbito dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Qualidade do Pré-natal**: A variável `CONSULTAS` (número de consultas de pré-natal) é um importante preditor, mas a qualidade dessas consultas não é capturada pelo sistema.
*   **Subnotificação de Anomalias**: Anomalias congênitas podem ser subnotificadas, especialmente aquelas que não são aparentes no momento do nascimento.
*   **Dados do Pai**: As informações sobre o pai (`IDADEPAI`, `ESCPAI`) são frequentemente mal preenchidas ou ignoradas, limitando análises que o incluam.
*   **Cobertura**: A cobertura do SINASC é considerada excelente na maior parte do Brasil, superando os registros civis em muitas localidades. No entanto, podem existir bolsões de sub-registro em áreas mais remotas.

## 7. Referências

1.  Morsoleto, R., et al. (2025). Prediction of Infant Mortality in Brazil using Machine Learning and Entity Matching on Brazilian Unified Health System’s Data. *Proceedings of the 13th Symposium on Knowledge Discovery, Mining and Learning*.
2.  Beluzo, C. E., et al. (2020). Machine Learning to Predict Neonatal Mortality Using Public Health Data from São Paulo - Brazil. *medRxiv*.
3.  Ministério da Saúde (BR), Departamento de Informática do SUS. Sistema de Informações sobre Nascidos Vivos (SINASC). Disponível em: [https://datasus.saude.gov.br/sistemas-e-aplicativos/epidemiologicos/sinasc/](https://datasus.saude.gov.br/sistemas-e-aplicativos/epidemiologicos/sinasc/)
