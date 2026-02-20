> [!PRIMARY]
> **CNES - Cadastro Nacional de Estabelecimentos de Saúde**
> O CNES não é um sistema de dados de pacientes, mas sim um registro da infraestrutura de saúde. Seu valor para a modelagem preditiva é indireto, mas poderoso: ele fornece **features contextuais** que descrevem o ambiente de cuidado onde o paciente está inserido. Essas features podem ser cruciais para explicar variações nos desfechos que não são capturadas apenas pelos dados do paciente.

# Análise do CNES para Modelagem Preditiva com IA

## 1. Descrição Geral

O Cadastro Nacional de Estabelecimentos de Saúde (CNES) é o sistema de informação oficial que cadastra todos os estabelecimentos de saúde, públicos ou privados, em território nacional. Ele contém informações detalhadas sobre a infraestrutura, recursos humanos, equipamentos, serviços e leitos de cada hospital, clínica, posto de saúde, etc.

## 2. Potencial para Predição com Machine Learning

O CNES não contém dados de pacientes. Seu uso em machine learning é para **enriquecer** outros datasets (como SIH, SIM, SINASC) com variáveis que caracterizam o estabelecimento de saúde. Ao fazer o *linkage* pelo código do estabelecimento (`CO_CNES`), pode-se adicionar features como:

*   **Nível de Complexidade do Hospital**: Prever desfechos de internações (do SIH) levando em conta se o hospital é de alta complexidade, se possui UTI, etc.
*   **Disponibilidade de Recursos**: Modelar o impacto da disponibilidade de equipamentos (ex: tomógrafo, ressonância magnética) na sobrevida de pacientes.
*   **Características da Equipe de Saúde**: Analisar como a razão entre número de médicos/enfermeiros e o número de leitos influencia a taxa de mortalidade hospitalar.
*   **Contexto Geográfico**: Usar a localização do estabelecimento para fazer o linkage com dados socioeconômicos do censo (IBGE), enriquecendo os modelos com variáveis de contexto social.

## 3. Estrutura e Variáveis para Features

O CNES é composto por várias tabelas (leitos, equipamentos, profissionais, etc.). As mais relevantes para criar features contextuais são:

| Tabela CNES | Variáveis Principais | Potencial como Feature (após agregação por CNES) |
| :--- | :--- | :--- |
| **Estabelecimento** | `TP_UNIDADE`, `NIV_HIERAR`, `TP_GESTAO` | Tipo de unidade (hospital, posto), gestão (pública/privada) |
| **Leitos** | `TP_LEITO`, `QT_EXIST`, `QT_SUS` | Número de leitos de UTI, cirúrgicos, clínicos, etc. |
| **Equipamentos** | `TP_EQUIP`, `QT_EXIST` | Presença/ausência de equipamentos-chave (Tomógrafo, etc.) |
| **Profissionais** | `CBO_ESPEC` (Especialidade), `VINCULACAO` | Contagem de especialistas (cardiologistas, oncologistas) |
| **Serviços** | `TP_SERVICO`, `CLASSIFICACAO` | Informa se o hospital oferece serviços como oncologia, cardiologia, etc. |

## 4. Identificadores e Record Linkage

O linkage com o CNES é **determinístico** e relativamente simples.

*   **Identificador Chave**: A variável `CO_CNES` (ou variações como `CNES_HOSP` no SIH) está presente na maioria dos sistemas de informação do DataSUS (SIH, SIA, SINASC, etc.) e identifica o estabelecimento onde o atendimento ocorreu.
*   **Processo de Linkage**: Basta juntar (fazer um *join*) a base de dados do paciente (ex: SIH) com as tabelas do CNES usando o código `CO_CNES` como chave. Como um mesmo CNES pode ter múltiplos registros (ex: vários tipos de leitos), é necessário agregar os dados do CNES para criar uma única linha de features por estabelecimento (ex: `total_leitos_uti`, `possui_tomografo_sim_nao`).

## 5. Construção de Janelas de Cohort

O CNES é geralmente usado de forma transversal. Para uma coorte de pacientes de um determinado ano, utiliza-se a "fotografia" do CNES daquele mesmo ano para caracterizar os estabelecimentos.

*   **Exemplo (Enriquecendo o SIH com dados do CNES)**:
    *   **Coorte**: Internações (AIHs) do SIH de 2022.
    *   **Dados de Contexto**: Tabelas do CNES referentes a 2022.
    *   **Processo**: 
        1.  Para cada `CO_CNES` no SIH, buscar as informações correspondentes no CNES.
        2.  Agregar os dados do CNES. Por exemplo, a partir da tabela de leitos, criar uma variável `num_leitos_uti` para cada `CO_CNES`.
        3.  Juntar essa nova variável à base do SIH. Agora, cada internação terá, além dos dados do paciente, as características do hospital onde ela ocorreu.

## 6. Limitações e Considerações

*   **Atualização**: O CNES é atualizado mensalmente, mas a qualidade da atualização depende do gestor local. Pode haver defasagem entre a realidade do estabelecimento e o que está registrado no sistema.
*   **Dados Agregados**: As informações são sobre o estabelecimento como um todo, não sobre o cuidado específico que um paciente recebeu. Um hospital pode ter uma UTI, mas o paciente em questão pode não ter sido admitido nela.
*   **Complexidade da Estrutura**: O CNES é um banco de dados relacional complexo, com dezenas de tabelas. Extrair e agregar as informações de forma correta exige um bom entendimento de sua estrutura.

## 7. Referências

1.  Ministério da Saúde (BR), Departamento de Informática do SUS. Cadastro Nacional de Estabelecimentos de Saúde (CNES). Disponível em: [https://cnes.datasus.gov.br/](https://cnes.datasus.gov.br/)
