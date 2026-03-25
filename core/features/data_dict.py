"""Dicionário de dados para as features de cada fonte DataSUS."""

from __future__ import annotations

# ── SINASC ────────────────────────────────────────────────────────────────────
_SINASC: dict[str, dict] = {
    "GRAVIDEZ": {
        "label": "Tipo de Gravidez",
        "desc": "Classificação do número de fetos: Única (1), Dupla (2), Tripla e mais (3).",
        "type": "Categórica",
        "values": {"1": "Única", "2": "Dupla", "3": "Tripla e mais"},
    },
    "PARTO": {
        "label": "Tipo de Parto",
        "desc": "Tipo de parto realizado: Vaginal (1), Cesáreo (2).",
        "type": "Categórica",
        "values": {"1": "Vaginal", "2": "Cesáreo"},
    },
    "CONSULTAS": {
        "label": "Consultas Pré-Natal",
        "desc": "Número de consultas de pré-natal realizadas: Nenhuma (1), 1–3 (2), 4–6 (3), 7 ou mais (4).",
        "type": "Ordinal",
        "values": {"1": "Nenhuma", "2": "1–3 consultas", "3": "4–6 consultas", "4": "7 ou mais", "9": "Ignorado"},
    },
    "IDADEMAE": {
        "label": "Idade da Mãe",
        "desc": "Idade da mãe em anos completos na data do parto.",
        "type": "Numérica",
    },
    "ESCMAE": {
        "label": "Escolaridade da Mãe",
        "desc": "Anos de estudo da mãe: Nenhuma (1), 1–3 anos (2), 4–7 anos (3), 8–11 anos (4), 12+ anos (5), Ignorado (9).",
        "type": "Ordinal",
        "values": {"1": "Sem escolaridade", "2": "1–3 anos", "3": "4–7 anos", "4": "8–11 anos", "5": "12 ou mais anos", "9": "Ignorado"},
    },
    "RACACORMAE": {
        "label": "Raça/Cor da Mãe",
        "desc": "Raça ou cor da pele da mãe: Branca (1), Preta (2), Amarela (3), Parda (4), Indígena (5).",
        "type": "Categórica",
        "values": {"1": "Branca", "2": "Preta", "3": "Amarela", "4": "Parda", "5": "Indígena"},
    },
    "ESTCIVMAE": {
        "label": "Estado Civil da Mãe",
        "desc": "Estado civil da mãe: Solteira (1), Casada (2), Viúva (3), Separada (4), União consensual (5).",
        "type": "Categórica",
        "values": {"1": "Solteira", "2": "Casada", "3": "Viúva", "4": "Separada judicialmente", "5": "União consensual"},
    },
    "SEXO": {
        "label": "Sexo do Recém-Nascido",
        "desc": "Sexo registrado ao nascer: Masculino (1), Feminino (2), Ignorado (0).",
        "type": "Categórica",
        "values": {"0": "Ignorado", "1": "Masculino", "2": "Feminino"},
    },
    "TPAPRESENT": {
        "label": "Tipo de Apresentação",
        "desc": "Posição do feto no parto: Cefálica (1), Pélvica/Podálica (2), Transversa (3).",
        "type": "Categórica",
        "values": {"1": "Cefálica", "2": "Pélvica/podálica", "3": "Transversa"},
    },
    "STTRABPART": {
        "label": "Trabalho de Parto Induzido",
        "desc": "Indica se o trabalho de parto foi induzido: Sim (1), Não (2), Não se aplica (3).",
        "type": "Categórica",
        "values": {"1": "Sim", "2": "Não", "3": "Não se aplica"},
    },
    "STCESPARTO": {
        "label": "Cesárea Prévia ao Trabalho de Parto",
        "desc": "Indica se a cesárea ocorreu antes do início do trabalho de parto: Sim (1), Não (2), Não se aplica (3).",
        "type": "Categórica",
        "values": {"1": "Sim", "2": "Não", "3": "Não se aplica"},
    },
    "IDANOMAL": {
        "label": "Anomalia Congênita",
        "desc": "Presença de anomalia congênita detectada ao nascimento: Sim (1), Não (2).",
        "type": "Categórica",
        "values": {"1": "Sim", "2": "Não"},
    },
    "PESO": {
        "label": "Peso ao Nascer",
        "desc": "Peso do recém-nascido em gramas na ocasião do parto.",
        "type": "Numérica",
    },
    "GESTACAO": {
        "label": "Semanas de Gestação",
        "desc": "Duração da gestação em semanas: < 22 sem (1), 22–27 sem (2), 28–31 sem (3), 32–36 sem (4), 37–41 sem (5), 42+ sem (6).",
        "type": "Ordinal",
        "values": {"1": "< 22 semanas", "2": "22–27 semanas", "3": "28–31 semanas", "4": "32–36 semanas", "5": "37–41 semanas", "6": "42 ou mais semanas"},
    },
    "APGAR1": {
        "label": "Apgar no 1º Minuto",
        "desc": "Escore de Apgar avaliado no 1º minuto de vida (0–10). Valores ≤ 6 indicam necessidade de atenção.",
        "type": "Numérica",
    },
    "APGAR5": {
        "label": "Apgar no 5º Minuto",
        "desc": "Escore de Apgar avaliado no 5º minuto de vida (0–10). Principal preditor de desfecho neonatal.",
        "type": "Numérica",
    },
    "CODANOMAL": {
        "label": "Código da Anomalia (CID-10)",
        "desc": "Código CID-10 da anomalia congênita identificada.",
        "type": "Categórica",
    },
    "PARTO_INST": {
        "label": "Local do Parto",
        "desc": "Local onde ocorreu o parto: Hospital (1), Outro estabelecimento de saúde (2), Domicílio (3), Outros (4).",
        "type": "Categórica",
        "values": {"1": "Hospital", "2": "Outro estab. de saúde", "3": "Domicílio", "4": "Outros"},
    },
    "preterm": {
        "label": "Prematuridade",
        "desc": "Indica se o parto foi pré-termo (< 37 semanas de gestação). Variável binária derivada de GESTACAO.",
        "type": "Derivada",
        "values": {"0": "Não pré-termo (≥ 37 sem)", "1": "Pré-termo (< 37 sem)"},
    },
    "low_birth_weight": {
        "label": "Baixo Peso",
        "desc": "Indica se o peso ao nascer foi inferior a 2.500g. Variável binária derivada de PESO.",
        "type": "Derivada",
        "values": {"0": "Peso adequado (≥ 2500g)", "1": "Baixo peso (< 2500g)"},
    },
    "age_group_mae": {
        "label": "Faixa Etária da Mãe",
        "desc": "Faixa etária da mãe derivada de IDADEMAE: adolescente (<18), adulta jovem (18–34), tardia (≥35).",
        "type": "Derivada",
        "values": {"1": "Adolescente (< 18 anos)", "2": "Adulta jovem (18–34 anos)", "3": "Tardia (≥ 35 anos)"},
    },
    "UF_SIGLA": {
        "label": "Unidade da Federação",
        "desc": "Sigla do estado onde ocorreu o nascimento.",
        "type": "Categórica",
    },
    "CODMUNNASC": {
        "label": "Município de Nascimento",
        "desc": "Código IBGE do município onde ocorreu o nascimento.",
        "type": "Categórica",
    },
    "KOTELCHUCK": {
        "label": "Índice de Kotelchuck (derivado)",
        "desc": "Índice de adequação do pré-natal baseado em consultas e semana de início. Derivado de CONSULTAS e MESPRENAT.",
        "type": "Derivada",
    },
}

# ── SIH ───────────────────────────────────────────────────────────────────────
_SIH: dict[str, dict] = {
    "DIAG_PRINC": {
        "label": "Diagnóstico Principal (CID-10)",
        "desc": "Código CID-10 do diagnóstico principal que motivou a internação hospitalar.",
        "type": "Categórica",
    },
    "DIAG_SEC": {
        "label": "Diagnóstico Secundário (CID-10)",
        "desc": "Código CID-10 de diagnóstico secundário, comorbidade ou complicação.",
        "type": "Categórica",
    },
    "IDADE": {
        "label": "Idade do Paciente",
        "desc": "Idade do paciente em anos completos na data da internação.",
        "type": "Numérica",
    },
    "SEXO": {
        "label": "Sexo do Paciente",
        "desc": "Sexo do paciente: Masculino (1), Feminino (3), Ignorado (0).",
        "type": "Categórica",
    },
    "RACA_COR": {
        "label": "Raça/Cor do Paciente",
        "desc": "Classificação étnico-racial do paciente internado: Branca (1), Preta (2), Amarela (3), Parda (4), Indígena (5).",
        "type": "Categórica",
        "values": {"1": "Branca", "2": "Preta", "3": "Amarela", "4": "Parda", "5": "Indígena"},
    },
    "CAR_INT": {
        "label": "Caráter da Internação",
        "desc": "Tipo de admissão hospitalar: Eletiva (01), Urgência (02), Acidente (03), entre outros.",
        "type": "Categórica",
        "values": {"01": "Eletiva", "02": "Urgência", "03": "Acidente", "04": "Outros"},
    },
    "PROC_REA": {
        "label": "Procedimento Realizado",
        "desc": "Descrição do procedimento principal realizado durante a internação.",
        "type": "Categórica",
    },
    "proc_rea_code": {
        "label": "Código do Procedimento",
        "desc": "Código numérico SIGTAP do procedimento principal realizado.",
        "type": "Categórica",
    },
    "DIAS_PERM": {
        "label": "Dias de Permanência",
        "desc": "Número total de dias de internação hospitalar.",
        "type": "Numérica",
    },
    "length_of_stay_days": {
        "label": "Dias de Permanência",
        "desc": "Total de dias que o paciente ficou internado. Variável derivada de DIAS_PERM.",
        "type": "Numérica",
    },
    "UTI_MES_TO": {
        "label": "Dias em UTI",
        "desc": "Total de dias que o paciente permaneceu em UTI durante a internação.",
        "type": "Numérica",
    },
    "used_icu": {
        "label": "Uso de UTI",
        "desc": "Indica se o paciente utilizou leito de UTI. Variável binária derivada de UTI_MES_TO.",
        "type": "Derivada",
        "values": {"0": "Não utilizou UTI", "1": "Utilizou UTI"},
    },
    "n_diag_sec": {
        "label": "Diagnósticos Secundários",
        "desc": "Quantidade de condições clínicas secundárias registradas além do diagnóstico principal.",
        "type": "Numérica",
    },
    "VAL_TOT": {
        "label": "Valor Total",
        "desc": "Valor total pago pelo SUS pela Autorização de Internação Hospitalar, em reais.",
        "type": "Numérica",
    },
    "CNES": {
        "label": "Estabelecimento (CNES)",
        "desc": "Código do estabelecimento de saúde no Cadastro Nacional de Estabelecimentos de Saúde.",
        "type": "Categórica",
    },
    "MUNIC_RES": {
        "label": "Município de Residência",
        "desc": "Código IBGE do município de residência do paciente.",
        "type": "Categórica",
    },
    "NAT_JUR": {
        "label": "Natureza Jurídica",
        "desc": "Natureza jurídica do estabelecimento: pública, privada, filantrópica, etc.",
        "type": "Categórica",
    },
    "COBRANCA": {
        "label": "Motivo de Cobrança",
        "desc": "Motivo de cobrança da AIH.",
        "type": "Categórica",
    },
    "COMPLEX": {
        "label": "Complexidade",
        "desc": "Nível de complexidade do atendimento: atenção básica, média complexidade, alta complexidade.",
        "type": "Ordinal",
    },
    "diag_chapter": {
        "label": "Capítulo CID-10",
        "desc": "Grande grupo de doenças segundo a CID-10, derivado de DIAG_PRINC. Ex: A–B = Infecciosas, C = Neoplasias.",
        "type": "Derivada",
    },
    "diag_block": {
        "label": "Bloco CID-10",
        "desc": "Agrupamento específico de diagnósticos dentro de um capítulo CID-10, derivado de DIAG_PRINC.",
        "type": "Derivada",
    },
    "age_group": {
        "label": "Faixa Etária",
        "desc": "Faixa etária do paciente derivada de IDADE: neonato (<28d), lactente, pré-escolar, escolar, adolescente, adulto jovem, adulto, idoso.",
        "type": "Derivada",
    },
}

# ── SIM ───────────────────────────────────────────────────────────────────────
_SIM: dict[str, dict] = {
    "CAUSABAS": {
        "label": "Causa Básica de Óbito (CID-10)",
        "desc": "Código CID-10 da causa básica de morte conforme a Declaração de Óbito.",
        "type": "Categórica",
    },
    "IDADE": {
        "label": "Idade",
        "desc": "Idade do falecido.",
        "type": "Numérica",
    },
    "SEXO": {
        "label": "Sexo",
        "desc": "Sexo do falecido: Masculino (1), Feminino (2), Ignorado (0).",
        "type": "Categórica",
    },
    "RACACOR": {
        "label": "Raça/Cor",
        "desc": "Raça ou cor da pele: Branca (1), Preta (2), Amarela (3), Parda (4), Indígena (5).",
        "type": "Categórica",
    },
    "LOCOCOR": {
        "label": "Local de Óbito",
        "desc": "Local onde ocorreu o óbito: Hospital (1), Outros estab. saúde (2), Domicílio (3), Via pública (4), Outros (5).",
        "type": "Categórica",
    },
}

# ── SINAN — Tuberculose ────────────────────────────────────────────────────────
_SINAN_TB: dict[str, dict] = {
    "NU_ANO": {
        "label": "Ano de Notificação",
        "desc": "Ano em que o caso foi notificado ao SINAN.",
        "type": "Numérica",
    },
    "CS_SEXO": {
        "label": "Sexo",
        "desc": "Sexo do paciente: Masculino (M), Feminino (F), Ignorado (I).",
        "type": "Categórica",
    },
    "NU_IDADE_N": {
        "label": "Idade",
        "desc": "Idade do paciente no momento da notificação.",
        "type": "Numérica",
    },
    "CS_RACA": {
        "label": "Raça/Cor",
        "desc": "Raça ou cor da pele: Branca (1), Preta (2), Amarela (3), Parda (4), Indígena (5), Ignorada (9).",
        "type": "Categórica",
    },
    "CS_ESCOL_N": {
        "label": "Escolaridade",
        "desc": "Escolaridade em anos de estudo: Analfabeto (0), 1–3 anos (1), 4–7 anos (2), 8–11 anos (3), 12+ anos (4), N/A (5), Ignorado (9).",
        "type": "Ordinal",
    },
    "idade_anos": {
        "label": "Idade em Anos",
        "desc": "Idade do paciente notificado em anos completos.",
        "type": "Numérica",
    },
    "FORMA": {
        "label": "Forma da Doença",
        "desc": "Apresentação clínica da tuberculose: Pulmonar (1), Extrapulmonar (2), Pulmonar + Extrapulmonar (3).",
        "type": "Categórica",
    },
    "BACILOSC_E": {
        "label": "Baciloscopia de Escarro",
        "desc": "Resultado do exame de baciloscopia na entrada: Positivo (1), Negativo (2), Não realizado (3), Não se aplica (4).",
        "type": "Categórica",
    },
    "CULTURA_ES": {
        "label": "Cultura de Escarro",
        "desc": "Resultado do exame de cultura para micobactéria: Positivo (1), Negativo (2), Em andamento (3), Não realizado (4).",
        "type": "Categórica",
    },
    "TRAT_SUPER": {
        "label": "Tratamento Supervisionado (TDO)",
        "desc": "Indica se o paciente recebe Tratamento Diretamente Observado: Sim, diário (1), Sim, semanal (2), Não (3).",
        "type": "Categórica",
    },
    "dot": {
        "label": "Tratamento Observado",
        "desc": "Indica se o tratamento foi acompanhado diretamente por profissional de saúde (DOTS). Derivado de TRAT_SUPER.",
        "type": "Derivada",
        "values": {"0": "Não supervisionado", "1": "Supervisionado"},
    },
    "ANTIRETRO": {
        "label": "Uso de Antirretrovirais",
        "desc": "Uso de terapia antirretroviral (TARV): Sim (1), Não (2), Não se aplica (3).",
        "type": "Categórica",
    },
    "HIV": {
        "label": "Coinfecção HIV",
        "desc": "Resultado da testagem para HIV: Positivo (1), Negativo (2), Em andamento (3), Não realizado (4).",
        "type": "Categórica",
    },
    "hiv_pos": {
        "label": "Teste de HIV",
        "desc": "Indica se o paciente realizou o teste HIV e seu resultado. Derivado de HIV.",
        "type": "Derivada",
        "values": {"0": "Negativo/Não realizado", "1": "Positivo"},
    },
    "AGRAVAIDS": {
        "label": "Coinfecção AIDS",
        "desc": "Indica se o paciente possui diagnóstico de AIDS associado à tuberculose: Sim (1), Não (2).",
        "type": "Categórica",
        "values": {"1": "Sim", "2": "Não"},
    },
    "DIABETES": {
        "label": "Diabetes",
        "desc": "Comorbidade: Diabetes mellitus — Sim (1), Não (2), Ignorado (9).",
        "type": "Categórica",
    },
    "ALCOOLISMO": {
        "label": "Alcoolismo",
        "desc": "Comorbidade: Alcoolismo — Sim (1), Não (2), Ignorado (9).",
        "type": "Categórica",
    },
    "POPULIT": {
        "label": "Populações Vulneráveis",
        "desc": "Pertence a população em situação de rua, privada de liberdade ou indígena.",
        "type": "Categórica",
    },
    "SITUA_ENCE": {
        "label": "Situação de Encerramento",
        "desc": "Desfecho do tratamento: Cura (1), Abandono (2), Óbito TB (3), Óbito outras causas (4), Transferência (5), Falência (6), TB-DR (7).",
        "type": "Categórica",
    },
    "RAIOX_TORA": {
        "label": "Raio-X de Tórax",
        "desc": "Resultado da imagem radiológica de tórax: Suspeito (1), Normal (2), Outros (3), Não realizado (4).",
        "type": "Categórica",
    },
    "age_group": {
        "label": "Faixa Etária",
        "desc": "Faixa etária derivada de NU_IDADE_N.",
        "type": "Derivada",
    },
}

# ── SINAN — Hanseníase ─────────────────────────────────────────────────────────
_SINAN_HANS: dict[str, dict] = {
    "FORMACLINI": {
        "label": "Forma Clínica",
        "desc": "Classificação clínica da hanseníase: Indeterminada (1), Tuberculoide (2), Dimorfa (3), Virchowiana (4).",
        "type": "Categórica",
        "values": {"1": "Indeterminada", "2": "Tuberculoide", "3": "Dimorfa", "4": "Virchowiana"},
    },
    "mb": {
        "label": "Classificação Operacional",
        "desc": "Categoria para fins de tratamento: Paucibacilar (1), Multibacilar (2).",
        "type": "Categórica",
        "values": {"1": "Paucibacilar", "2": "Multibacilar"},
    },
    "grau_incapacidade": {
        "label": "Grau de Incapacidade",
        "desc": "Avaliação do grau de incapacidade física no diagnóstico: Grau 0, Grau 1, Grau 2.",
        "type": "Ordinal",
        "values": {"0": "Grau 0", "1": "Grau 1", "2": "Grau 2"},
    },
    "MODOENTR": {
        "label": "Modo de Entrada",
        "desc": "Como o caso entrou no sistema: Caso novo (1), Recidiva (2), Transferência (3), Outros (4).",
        "type": "Categórica",
        "values": {"1": "Caso novo", "2": "Recidiva", "3": "Transferência", "4": "Outros"},
    },
    "MODODETECT": {
        "label": "Modo de Detecção",
        "desc": "Como a doença foi descoberta: Demanda espontânea (1), Exame de contatos (2), Exame coletivo (3), Outros (4).",
        "type": "Categórica",
        "values": {"1": "Demanda espontânea", "2": "Exame de contatos", "3": "Exame coletivo", "4": "Outros"},
    },
    "BACILOSCOP": {
        "label": "Baciloscopia",
        "desc": "Resultado do exame baciloscópico: Positivo (1), Negativo (2), Não realizado (3).",
        "type": "Categórica",
    },
    "ESQ_INI_N": {
        "label": "Esquema Terapêutico",
        "desc": "Medicamentos iniciais prescritos (PQT): Adulto Paucibacilar (1), Adulto Multibacilar (2), Criança Paucibacilar (3), Criança Multibacilar (4).",
        "type": "Categórica",
        "values": {"1": "PQT Adulto PB", "2": "PQT Adulto MB", "3": "PQT Criança PB", "4": "PQT Criança MB"},
    },
}

# ── SINAN — Dengue / Arboviroses ───────────────────────────────────────────────
_SINAN_DENGUE: dict[str, dict] = {
    "CS_SEXO": {
        "label": "Sexo",
        "desc": "Sexo do paciente: Masculino (M), Feminino (F).",
        "type": "Categórica",
    },
    "NU_IDADE_N": {
        "label": "Idade",
        "desc": "Idade do paciente na data de notificação.",
        "type": "Numérica",
    },
    "CS_RACA": {
        "label": "Raça/Cor",
        "desc": "Raça ou cor da pele: Branca (1), Preta (2), Amarela (3), Parda (4), Indígena (5).",
        "type": "Categórica",
    },
    "FEBRE": {
        "label": "Febre",
        "desc": "Presença de febre: Sim (1), Não (2).",
        "type": "Categórica",
    },
    "MIALGIA": {
        "label": "Mialgia",
        "desc": "Presença de mialgia (dor muscular): Sim (1), Não (2).",
        "type": "Categórica",
    },
    "CEFALEIA": {
        "label": "Cefaleia",
        "desc": "Presença de cefaleia: Sim (1), Não (2).",
        "type": "Categórica",
    },
    "EXANTEMA": {
        "label": "Exantema",
        "desc": "Presença de exantema (erupção cutânea): Sim (1), Não (2).",
        "type": "Categórica",
    },
    "VOMITO": {
        "label": "Vômito",
        "desc": "Presença de vômito: Sim (1), Não (2).",
        "type": "Categórica",
    },
    "NAUSEA": {
        "label": "Náusea",
        "desc": "Presença de náusea: Sim (1), Não (2).",
        "type": "Categórica",
    },
    "DOR_COSTAS": {
        "label": "Dor nas Costas",
        "desc": "Presença de dor nas costas/retrorbital: Sim (1), Não (2).",
        "type": "Categórica",
    },
    "CLASSI_FIN": {
        "label": "Classificação Final",
        "desc": "Classificação final do caso: Dengue sem sinais de alarme (5), Dengue com sinais de alarme (6), Dengue grave (7), Descartado (11).",
        "type": "Categórica",
    },
    "HOSPITALIZ": {
        "label": "Hospitalização",
        "desc": "Paciente foi hospitalizado: Sim (1), Não (2).",
        "type": "Categórica",
    },
    "SOROTIPO": {
        "label": "Sorotipo",
        "desc": "Sorotipo do vírus identificado: DEN 1, DEN 2, DEN 3, DEN 4.",
        "type": "Categórica",
    },
}

# ── Dicionário unificado ───────────────────────────────────────────────────────
FEATURE_DICT: dict[str, dict] = {}
for _d in (_SINASC, _SIH, _SIM, _SINAN_TB, _SINAN_HANS, _SINAN_DENGUE):
    FEATURE_DICT.update(_d)


def get_info(feature: str) -> dict | None:
    """Return dict with label, desc, type — or None if not found."""
    return FEATURE_DICT.get(feature) or FEATURE_DICT.get(feature.upper())
