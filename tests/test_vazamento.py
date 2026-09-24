"""Features sugeridas sem vazamento (PRED-04, ML-05, DESF-04, DESF-09).

Falha se uma feature proibida voltar à lista suggested_features de um
desfecho. A lista proibida depende do momento da predição:

- desfechos do SIH previstos na admissão não podem usar o que só existe na
  alta (permanência, diárias, UTI, valor total, diagnóstico secundário,
  procedimento realizado). Readmissão em 30 dias prevê na alta, então ali
  esses campos são informação legítima e o desfecho fica fora da regra;
- dengue e chikungunya não podem usar sinais de alarme, critérios de
  gravidade nem hospitalização, que definem o desfecho ou decorrem dele.
"""

from __future__ import annotations

import importlib

import pytest

from core.outcomes import _REGISTRY


def _instancia(key: str):
    meta = _REGISTRY[key]
    return getattr(importlib.import_module(meta["module"]), meta["class"])()


# Campos do SIH-RD (brutos e derivados) que só ficam conhecidos na alta.
SIH_SO_NA_ALTA = {
    "length_of_stay_days", "DIARIAS", "QT_DIARIAS", "DIAS_PERM",
    "VAL_TOT", "VAL_UTI", "UTI_MES_TO", "UTI_INT_TO", "used_icu",
    "n_diag_sec", "DIAG_SEC", "DIAG_SECUN", "DIAGSEC1",
    "PROC_REA", "proc_rea_code",
    "DT_SAIDA", "MORTE", "is_death",
}
# Desfechos do SIH com predição na alta, onde os campos acima são legítimos.
SIH_PREDICAO_NA_ALTA = {"readmissao_30d"}

SIH_NA_ADMISSAO = sorted(
    key for key, meta in _REGISTRY.items()
    if "SIH" in meta["data_sources"] and key not in SIH_PREDICAO_NA_ALTA
)

# Arboviroses: sinais de alarme (layout antigo e ALRM_*), gravidade (GRAV_*) e
# internação.
ARBO_PROIBIDAS = {
    "hospitalizado", "HOSPITALIZ", "DT_INTERNA",
    "DOR_ABDOM", "VOMITO_2", "SANG_MUC", "VERTIG", "PRESSAO",
    "CHOQUE", "CONVULSAO", "INSUF_RESP",
}
ARBO_PREFIXOS_PROIBIDOS = ("ALRM_", "GRAV_")
ARBOVIROSES = ["dengue_grave", "chikungunya_hospitalizado"]


def test_lista_sih_na_admissao_cobre_os_desfechos_esperados():
    assert {
        "mortalidade_hospitalar", "permanencia_prolongada",
        "custo_elevado", "infeccao_hospitalar",
    } <= set(SIH_NA_ADMISSAO)


@pytest.mark.parametrize("key", SIH_NA_ADMISSAO)
def test_sih_na_admissao_sem_campos_da_alta(key):
    features = set(_instancia(key).suggested_features)
    vazamento = features & SIH_SO_NA_ALTA
    assert not vazamento, f"{key} usa campos que só existem na alta: {sorted(vazamento)}"


@pytest.mark.parametrize("key", ARBOVIROSES)
def test_arboviroses_sem_alarme_gravidade_ou_internacao(key):
    features = _instancia(key).suggested_features
    proibidas = sorted(
        f for f in features
        if f in ARBO_PROIBIDAS or f.startswith(ARBO_PREFIXOS_PROIBIDOS)
    )
    assert not proibidas, f"{key} usa campos que definem ou decorrem do desfecho: {proibidas}"


@pytest.mark.parametrize("key", sorted(_REGISTRY))
def test_alvo_nunca_e_feature(key):
    outcome = _instancia(key)
    assert outcome.target_col not in outcome.suggested_features


def test_descricao_de_mortalidade_hospitalar_e_intra_hospitalar():
    outcome = _instancia("mortalidade_hospitalar")
    assert "intra-hospitalar" in outcome.description
    assert "30 dias após a alta" not in outcome.description
    assert "intra-hospitalar" in _REGISTRY["mortalidade_hospitalar"]["description"]
