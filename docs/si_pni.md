> [!PRIMARY]
> **SI-PNI - Sistema de Informação do Programa Nacional de Imunizações**
> O SI-PNI é a fonte de dados para a predição de desfechos relacionados à vacinação e à epidemiologia de doenças imunopreveníveis. Ele permite a construção de cohorts de vacinados e não vacinados, essencial para avaliar a efetividade de vacinas, identificar populações com baixa cobertura vacinal e prever o risco de surtos de doenças como sarampo, poliomielite e outras.

# Análise do SI-PNI para Modelagem Preditiva com IA

## 1. Descrição Geral

O Sistema de Informação do Programa Nacional de Imunizações (SI-PNI) é o sistema oficial para o registro de todas as doses de vacinas aplicadas no Brasil, tanto na rede pública quanto na privada. Ele coleta informações sobre o indivíduo vacinado, a vacina aplicada (tipo, dose, lote), a data da aplicação e o local. O SI-PNI é fundamental para o monitoramento da cobertura vacinal, a avaliação da efetividade das campanhas e a vigilância epidemiológica de doenças imunopreveníveis.

## 2. Potencial para Predição com Machine Learning

O SI-PNI é uma base de dados rica para a modelagem preditiva em saúde pública, com foco em imunização:

*   **Risco de Doença Imunoprevenível**: Prever a probabilidade de um indivíduo contrair uma doença imunoprevenível (ex: sarampo, coqueluche) com base em seu histórico vacinal e na cobertura vacinal da sua região.
*   **Efetividade Vacinal**: Avaliar a efetividade de diferentes vacinas ou esquemas vacinais na prevenção de doenças ou na redução da gravidade dos casos (requer linkage com bases de notificação como SINAN ou SIVEP-Gripe).
*   **Baixa Adesão Vacinal**: Identificar grupos populacionais ou indivíduos com maior risco de não completar o esquema vacinal recomendado, permitindo ações de busca ativa.
*   **Predição de Surtos**: Utilizar dados de cobertura vacinal e de ocorrência de casos (do SINAN) para prever o risco de surtos de doenças imunopreveníveis em determinadas áreas.

## 3. Estrutura e Variáveis para Features

O SI-PNI registra cada dose de vacina aplicada, permitindo a construção de um histórico vacinal detalhado.

| Categoria | Variáveis Principais | Potencial como Feature |
| :--- | :--- | :--- |
| **Paciente** | `paciente_id`, `cpf`, `cns`, `dt_nascimento`, `sexo` | Identificadores, demografia |
| **Vacinação** | `vacina_nome`, `dose_numero`, `dt_aplicacao`, `lote` | Tipo de vacina, número de doses, data da aplicação |
| **Local** | `estabelecimento_cnes`, `municipio_aplicacao` | Local onde a vacina foi aplicada |

## 4. Identificadores e Record Linkage

O SI-PNI possui bons identificadores, facilitando o linkage.

*   **Identificadores Disponíveis**: O **CNS** e o **CPF** são os principais identificadores do SI-PNI. Além disso, o sistema registra nome completo, data de nascimento e nome da mãe, o que permite o linkage probabilístico com outras bases.
*   **Necessidade de Record Linkage**:
    *   **SI-PNI - SINASC**: Para vincular o histórico vacinal da criança com suas condições de nascimento e desfechos neonatais.
    *   **SI-PNI - SINAN/SIVEP-Gripe**: Essencial para estudos de efetividade vacinal, comparando o status vacinal de pacientes que contraíram a doença com aqueles que não contraíram, ou que tiveram formas mais graves/leves.
    *   **SI-PNI - e-SUS AB**: Para integrar o histórico vacinal com o acompanhamento de saúde na atenção primária.

## 5. Construção de Janelas de Cohort

O SI-PNI é ideal para a construção de cohorts de vacinação.

*   **Exemplo (Efetividade da Vacina contra Sarampo)**:
    *   **Coorte**: Crianças nascidas em um determinado ano (identificadas via SINASC e linkadas com SI-PNI).
    *   **Observation Window**: Período até a criança completar o esquema vacinal para sarampo. As features incluem o status vacinal (vacinado/não vacinado, doses completas/incompletas) e dados demográficos.
    *   **Prediction Window**: Período de acompanhamento após a vacinação (ex: 5 anos).
    *   **Outcome**: Ocorrência de caso de sarampo (identificado via linkage com SINAN) dentro da *prediction window*? (Sim/Não).

## 6. Limitações e Considerações

*   **Dados Históricos**: A qualidade e a completude dos dados podem variar para anos mais antigos, antes da digitalização e consolidação do sistema.
*   **Migração de Dados**: A migração de dados de sistemas anteriores para o SI-PNI pode ter gerado inconsistências ou perdas de informação.
*   **Eventos Adversos Pós-Vacinação (EAPV)**: Embora o SI-PNI registre a aplicação da vacina, a notificação de EAPV é feita em outro sistema (e-SUS Notifica/VigiMed), exigindo linkage para estudos de segurança.
*   **Cobertura Vacinal**: A cobertura vacinal é um indicador importante, mas o SI-PNI permite ir além, analisando o histórico individual de cada paciente.

## 7. Referências

1.  Ministério da Saúde (BR), Departamento de Informática do SUS. Sistema de Informação do Programa Nacional de Imunizações (SI-PNI). Disponível em: [https://pni.datasus.gov.br/](https://pni.datasus.gov.br/)
2.  Ministério da Saúde (BR). Programa Nacional de Imunizações (PNI). Disponível em: [https://www.gov.br/saude/pt-br/vacinacao/programa-nacional-de-imunizacoes-pni](https://www.gov.br/saude/pt-br/vacinacao/programa-nacional-de-imunizacoes-pni)
