"""Dicionário de dados para as features de cada fonte DataSUS."""

from __future__ import annotations

# ── SINASC ────────────────────────────────────────────────────────────────────
_SINASC: dict[str, dict] = {
    "GRAVIDEZ": {
        "label": "Tipo de Gravidez",
        "desc": "Classificação do número de fetos: Única (1), Dupla (2), Tripla e mais (3).",
        "type": "Categórica",
    },
    "PARTO": {
        "label": "Tipo de Parto",
        "desc": "Tipo de parto realizado: Vaginal (1), Cesáreo (2).",
        "type": "Categórica",
    },
    "CONSULTAS": {
        "label": "Consultas Pré-Natal",
        "desc": "Número de consultas de pré-natal realizadas: Nenhuma (1), 1–3 (2), 4–6 (3), 7 ou mais (4).",
        "type": "Ordinal",
    },
    "IDADEMAE": {
        "label": "Idade da Mãe (anos)",
        "desc": "Idade da mãe em anos completos na data do parto.",
        "type": "Numérica",
    },
    "ESCMAE": {
        "label": "Escolaridade da Mãe",
        "desc": "Anos de estudo da mãe: Nenhuma (1), 1–3 anos (2), 4–7 anos (3), 8–11 anos (4), 12+ anos (5), Ignorado (9).",
        "type": "Ordinal",
    },
    "RACACORMAE": {
        "label": "Raça/Cor da Mãe",
        "desc": "Raça ou cor da pele da mãe: Branca (1), Preta (2), Amarela (3), Parda (4), Indígena (5).",
        "type": "Categórica",
    },
    "ESTCIVMAE": {
        "label": "Estado Civil da Mãe",
        "desc": "Estado civil da mãe: Solteira (1), Casada (2), Viúva (3), Separada (4), União consensual (5).",
        "type": "Categórica",
    },
    "SEXO": {
        "label": "Sexo do Recém-Nascido",
        "desc": "Sexo registrado ao nascer: Masculino (1), Feminino (2), Ignorado (0).",
        "type": "Categórica",
    },
    "TPAPRESENT": {
        "label": "Apresentação do RN",
        "desc": "Apresentação fetal durante o parto: Cefálica (1), Pélvica/podálica (2), Transversa (3).",
        "type": "Categórica",
    },
    "STTRABPART": {
        "label": "Trabalho de Parto Induzido",
        "desc": "Indica se o trabalho de parto foi induzido: Sim (1), Não (2), Não se aplica (3).",
        "type": "Categórica",
    },
    "STCESPARTO": {
        "label": "Cesárea antes do Trabalho de Parto",
        "desc": "Cesárea ocorreu antes do início do trabalho de parto: Sim (1), Não (2), Não se aplica (3).",
        "type": "Categórica",
    },
    "IDANOMAL": {
        "label": "Anomalia Congênita",
        "desc": "Presença de anomalia congênita detectada ao nascimento: Sim (1), Não (2).",
        "type": "Categórica",
    },
    "PESO": {
        "label": "Peso ao Nascer (gramas)",
        "desc": "Peso do recém-nascido em gramas na ocasião do parto.",
        "type": "Numérica",
    },
    "GESTACAO": {
        "label": "Semanas de Gestação",
        "desc": "Duração da gestação em semanas: < 22 sem (1), 22–27 sem (2), 28–31 sem (3), 32–36 sem (4), 37–41 sem (5), 42+ sem (6).",
        "type": "Ordinal",
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
    },
    "age_group_mae": {
        "label": "Faixa Etária da Mãe (derivada)",
        "desc": "Faixa etária da mãe derivada de IDADEMAE: adolescente (<18), adulta jovem (18–34), tardia (≥35). Variável criada durante o processamento.",
        "type": "Derivada",
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
        "label": "Idade (anos)",
        "desc": "Idade do paciente em anos completos na data da internação.",
        "type": "Numérica",
    },
    "SEXO": {
        "label": "Sexo",
        "desc": "Sexo do paciente: Masculino (1), Feminino (3), Ignorado (0).",
        "type": "Categórica",
    },
    "PROC_REA": {
        "label": "Procedimento Realizado",
        "desc": "Código SIGTAP do procedimento principal realizado durante a internação.",
        "type": "Categórica",
    },
    "DIAS_PERM": {
        "label": "Dias de Permanência",
        "desc": "Número total de dias de internação hospitalar.",
        "type": "Numérica",
    },
    "UTI_MES_TO": {
        "label": "Dias em UTI",
        "desc": "Total de dias que o paciente permaneceu em Unidade de Terapia Intensiva durante a internação.",
        "type": "Numérica",
    },
    "VAL_TOT": {
        "label": "Valor Total da AIH (R$)",
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
        "label": "Capítulo CID (derivado)",
        "desc": "Capítulo do CID-10 do diagnóstico principal (letra), derivado de DIAG_PRINC. Ex: A–B = Infecciosas, C = Neoplasias.",
        "type": "Derivada",
    },
    "age_group": {
        "label": "Faixa Etária (derivada)",
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
    "FORMA": {
        "label": "Forma Clínica",
        "desc": "Forma clínica da tuberculose: Pulmonar (1), Extrapulmonar (2), Pulmonar + Extrapulmonar (3).",
        "type": "Categórica",
    },
    "BACILOSC_E": {
        "label": "Baciloscopia de Escarro (entrada)",
        "desc": "Resultado da baciloscopia de escarro na entrada: Positivo (1), Negativo (2), Não realizada (3), Não se aplica (4).",
        "type": "Categórica",
    },
    "TRAT_SUPER": {
        "label": "Tratamento Supervisionado (TDO)",
        "desc": "Indica se o paciente recebe Tratamento Diretamente Observado: Sim, diário (1), Sim, semanal (2), Não (3).",
        "type": "Categórica",
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
    "age_group": {
        "label": "Faixa Etária (derivada)",
        "desc": "Faixa etária derivada de NU_IDADE_N.",
        "type": "Derivada",
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
for _d in (_SINASC, _SIH, _SIM, _SINAN_TB, _SINAN_DENGUE):
    FEATURE_DICT.update(_d)


def get_info(feature: str) -> dict | None:
    """Return dict with label, desc, type — or None if not found."""
    return FEATURE_DICT.get(feature) or FEATURE_DICT.get(feature.upper())
