> [!WARNING]
> O Record Linkage é uma etapa complexa e computacionalmente intensiva. A qualidade do resultado final depende diretamente da qualidade dos dados de identificação e da robustez do método escolhido. Sempre valide seus resultados com revisão clerical e métricas de acurácia.

# Guia de Record Linkage entre Bases do DataSUS

## 1. Por que o Record Linkage é Essencial?

A maioria dos sistemas de informação do DataSUS foi criada com um propósito específico (ex: registrar óbitos, internações, nascimentos) e, historicamente, não foram projetados para "conversar" entre si. Não existe um identificador único universal que perpasse todas as bases de dados. O **Record Linkage** (ou pareamento de registros) é o processo de identificar e vincular registros que se referem à mesma entidade (neste caso, o mesmo paciente) em diferentes arquivos ou bancos de dados.

Para a modelagem preditiva, o linkage é crucial para:

*   **Construir uma Visão Longitudinal**: Acompanhar um paciente ao longo do tempo e através de diferentes níveis de atenção (atenção primária, hospitalar, ambulatorial).
*   **Definir Desfechos (Outcomes)**: Vincular uma coorte de pacientes (ex: do SIH) com a base de óbitos (SIM) para verificar quem morreu.
*   **Enriquecer Features**: Adicionar informações de uma base a outra (ex: adicionar o histórico de vacinas do SI-PNI a uma coorte do SINASC).

## 2. Métodos de Linkage

Existem dois métodos principais para realizar o linkage:

### a) Linkage Determinístico

Consiste em vincular registros que possuem uma correspondência exata em um ou mais campos-chave. É mais simples e rápido, mas menos flexível a erros.

*   **Quando usar**: Quando se tem um identificador único e confiável, como o **CPF** ou o **CNS**. 
*   **Exemplo**: Vincular a base do SIVEP-Gripe com a do SI-PNI usando o CPF do paciente para avaliar a efetividade da vacina.
*   **Desvantagens**: Falha se houver qualquer erro de digitação ou se o campo estiver faltando. Um mesmo paciente com dois números de CNS diferentes não será pareado.

### b) Linkage Probabilístico

É o método mais robusto e amplamente utilizado para as bases do DataSUS. Ele não exige correspondência exata, mas calcula um "escore de semelhança" entre pares de registros com base em múltiplos campos (bloqueadores e comparadores). Pares com escore acima de um limiar são considerados "matches".

*   **Quando usar**: Na ausência de um identificador único confiável, utilizando uma combinação de campos como nome, data de nascimento e nome da mãe.
*   **Exemplo**: Vincular a base de nascidos vivos (SINASC) com a de óbitos (SIM) para encontrar os óbitos infantis.

## 3. Etapas do Linkage Probabilístico

O processo geralmente segue as seguintes etapas:

1.  **Pré-processamento (Limpeza e Padronização)**:
    *   Converter todos os campos para maiúsculas.
    *   Remover acentos, pontuações e caracteres especiais.
    *   Padronizar nomes (ex: remover preposições como "DE", "DA", "DOS").
    *   Aplicar algoritmos fonéticos (ex: **Soundex**, **Metaphone**) para criar códigos fonéticos para os nomes, tornando-os robustos a erros de grafia.
    *   Padronizar datas.

2.  **Bloqueio (Blocking)**:
    *   Para evitar a comparação de todos os registros de uma base com todos os da outra (o que seria computacionalmente inviável), a base é dividida em blocos menores.
    *   Apenas registros dentro do mesmo bloco são comparados.
    *   **Exemplos de chaves de bloqueio**: Código Soundex do primeiro nome + ano de nascimento; ou município de residência + sexo.

3.  **Comparação e Cálculo do Escore**:
    *   Dentro de cada bloco, os campos de comparação (ex: nome completo, data de nascimento, nome da mãe) são comparados usando algoritmos de similaridade de strings (ex: **Jaro-Winkler**, **Levenshtein**).
    *   Um peso é atribuído a cada campo, com base em sua capacidade de discriminação (o quão raro é um acordo naquele campo).
    *   O escore total para o par de registros é a soma dos pesos.

4.  **Classificação e Avaliação**:
    *   Dois limiares são definidos: um superior e um inferior.
    *   Pares com escore **acima do limiar superior** são classificados como **matches**.
    *   Pares com escore **abaixo do limiar inferior** são classificados como **non-matches**.
    *   Pares **entre os dois limiares** são classificados como **pares duvidosos** e requerem revisão clerical (manual).
    *   A acurácia do linkage é avaliada com métricas como sensibilidade, especificidade e valor preditivo positivo, geralmente usando uma amostra de pares revisados manualmente como padrão-ouro.

## 4. Ferramentas e Bibliotecas

*   **Python**: A biblioteca `recordlinkage` é uma das mais completas e bem documentadas para realizar linkage probabilístico em Python, integrando-se bem com o `pandas`.
*   **R**: O pacote `RecordLinkage` oferece funcionalidades semelhantes no ambiente R.
*   **Software Dedicado**: Ferramentas como o **RecLink** (desenvolvido no Brasil) e o **Febrl** (Freely Extensible Biomedical Record Linkage) são softwares especializados para essa tarefa.

## 5. Exemplo Prático: Linkage SINASC-SIM

1.  **Bases**: `SINASC.DBC` e `SIM.DBC` do mesmo estado e ano.
2.  **Pré-processamento**: Padronizar `NOMEMAE` (nome da mãe) e `DTNASC` (data de nascimento do bebê) em ambas as bases. Aplicar Soundex em `NOMEMAE`.
3.  **Bloqueio**: Criar blocos usando o código Soundex de `NOMEMAE`.
4.  **Comparação**: Comparar `NOMEMAE` (usando Jaro-Winkler) e `DTNASC` (comparação exata).
5.  **Classificação**: Calcular os escores e definir os limiares para identificar os pares correspondentes (bebês que nasceram e morreram).

## 6. Referências

1.  Guerra Junior, A. A., et al. (2018). Building the National Database of Health Centred on the Individual: Administrative and Epidemiological Record Linkage - Brazil, 2000-2015. *International Journal of Population Data Science*, 3(1).
2.  Python Record Linkage Toolkit Documentation. Disponível em: [https://recordlinkage.readthedocs.io/](https://recordlinkage.readthedocs.io/)
