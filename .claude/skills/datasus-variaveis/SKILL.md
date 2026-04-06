# Skill: Mapeamento de Variáveis DataSUS

Quando o usuário pedir para atualizar nomes/rótulos de variáveis no projeto datasus-ai-prediction,
use este mapeamento como fonte de verdade. O arquivo central é:
`core/features/data_dict.py` — cada entrada tem `label`, `desc`, `type` e opcionalmente `values`.

---

## SINASC — Saúde Materno-Infantil

| Variável         | label canônico                    | type      |
|------------------|-----------------------------------|-----------|
| GESTACAO         | Semanas de Gestação               | Ordinal   |
| GRAVIDEZ         | Tipo de Gravidez                  | Categórica|
| PARTO            | Tipo de Parto                     | Categórica|
| CONSULTAS        | Consultas Pré-Natal               | Ordinal   |
| IDADEMAE         | Idade da Mãe                      | Numérica  |
| ESCMAE           | Escolaridade da Mãe               | Ordinal   |
| RACACORMAE       | Raça/Cor da Mãe                   | Categórica|
| ESTCIVMAE        | Estado Civil da Mãe               | Categórica|
| SEXO             | Sexo do Recém-nascido             | Categórica|
| TPAPRESENT       | Tipo de Apresentação              | Categórica|
| STTRABPART       | Trabalho de Parto Induzido        | Categórica|
| STCESPARTO       | Cesárea Prévia ao Trabalho de Parto | Categórica|
| IDANOMAL         | Anomalia Congênita                | Categórica|
| PESO             | Peso ao Nascer                    | Numérica  |
| preterm          | Prematuridade                     | Derivada  |
| low_birth_weight | Baixo Peso                        | Derivada  |
| age_group_mae    | Faixa Etária da Mãe               | Derivada  |
| UF_SIGLA         | Unidade da Federação              | Categórica|

---

## SIH — Internação Hospitalar

| Variável           | label canônico                | type      |
|--------------------|-------------------------------|-----------|
| IDADE              | Idade do Paciente             | Numérica  |
| SEXO               | Sexo do Paciente              | Categórica|
| RACA_COR           | Raça/Cor do Paciente          | Categórica|
| CAR_INT            | Caráter da Internação         | Categórica|
| PROC_REA           | Procedimento Realizado        | Categórica|
| proc_rea_code      | Código do Procedimento        | Categórica|
| diag_chapter       | Capítulo CID-10               | Derivada  |
| diag_block         | Bloco CID-10                  | Derivada  |
| length_of_stay_days| Dias de Permanência           | Numérica  |
| used_icu           | Uso de UTI                    | Derivada  |
| n_diag_sec         | Diagnósticos Secundários      | Numérica  |
| VAL_TOT            | Valor Total                   | Numérica  |
| age_group          | Faixa Etária                  | Derivada  |

---

## SINAN — Tuberculose (SINAN_TB)

| Variável    | label canônico                | type      |
|-------------|-------------------------------|-----------|
| idade_anos  | Idade em Anos                 | Numérica  |
| CS_SEXO     | Sexo                          | Categórica|
| CS_RACA     | Raça/Cor                      | Categórica|
| CS_ESCOL_N  | Escolaridade                  | Ordinal   |
| FORMA       | Forma da Doença               | Categórica|
| BACILOSC_E  | Baciloscopia de Escarro       | Categórica|
| CULTURA_ES  | Cultura de Escarro            | Categórica|
| hiv_pos     | Teste de HIV                  | Categórica|
| AGRAVAIDS   | Coinfecção AIDS               | Categórica|
| dot         | Tratamento Observado (DOTS)   | Categórica|
| RAIOX_TORA  | Raio-X de Tórax               | Categórica|

---

## SINAN — Hanseníase (SINAN_HANS)

| Variável          | label canônico              | type      |
|-------------------|-----------------------------|-----------|
| FORMACLINI        | Forma Clínica               | Categórica|
| mb                | Classificação Operacional   | Categórica|
| grau_incapacidade | Grau de Incapacidade        | Ordinal   |
| MODOENTR          | Modo de Entrada             | Categórica|
| MODODETECT        | Modo de Detecção            | Categórica|
| BACILOSCOP        | Baciloscopia                | Categórica|
| ESQ_INI_N         | Esquema Terapêutico         | Categórica|

---

---

## Equivalências demográficas por base (equidade e estratificação)

Cada base usa nomes diferentes para as mesmas dimensões demográficas.
A análise de equidade (`pages/analise.py`) detecta automaticamente qual está presente na coorte.

| Dimensão     | SIH        | SINASC        | SINAN_*   |
|--------------|------------|---------------|-----------|
| Sexo         | `SEXO`     | `SEXO`        | `CS_SEXO` |
| Raça/Cor     | `RACA_COR` | `RACACORMAE`  | `CS_RACA` |
| Localização  | `UF_SIGLA` | `UF_SIGLA`    | —         |
| Faixa etária | `age_group`| `age_group_mae`| `age_group` |

Ao adicionar suporte a nova base, incluir os equivalentes em `_fairness_candidates` em `pages/analise.py`.

---

## Regras de aplicação

1. Ao encontrar uma variável DataSUS no código (label, tooltip, tabela, relatório), use o **label canônico** desta tabela.
2. Variáveis marcadas como `Derivada` são calculadas no pipeline — o label deve deixar isso claro sem a palavra "derivada" entre parênteses.
3. Se uma variável não constar nesta tabela, adicione-a aqui E em `core/features/data_dict.py`.
4. Nunca inclua o sufixo "(derivada)" ou "(anos)" no label — a coluna `type` e o `desc` já carregam essa informação.
5. Para equidade/estratificação: usar sempre a coluna nativa da base — não renomear `CS_SEXO` para `SEXO` nos dados brutos do SINAN.
