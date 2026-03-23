"""Outcomes registry — lightweight metadata only at import time.

Heavy outcome classes are imported lazily on first access, so the UI
renders immediately without waiting for all 17 modules + their data
preprocessors to load.
"""
from __future__ import annotations

# ── Metadata registry (no heavy imports) ─────────────────────────────────────

_REGISTRY: dict[str, dict] = {
    # Internação Hospitalar
    "mortalidade_hospitalar": {
        "module": "core.outcomes.mortalidade_hospitalar",
        "class":  "MortalidadeHospitalar",
        "name":   "Mortalidade Hospitalar",
        "description": "Prediz óbito durante a internação hospitalar usando dados do SIH linkados ao SIM.",
        "data_sources": ["SIH", "SIM"],
        "icon": "monitor_heart",
        "estimated_download_min": 15,
    },
    "readmissao_30d": {
        "module": "core.outcomes.readmissao_30d",
        "class":  "ReadmissaoHospitalar30d",
        "name":   "Readmissão Hospitalar 30 dias",
        "description": "Prediz se um paciente será reinternado em até 30 dias após a alta hospitalar.",
        "data_sources": ["SIH"],
        "icon": "sync",
        "estimated_download_min": 10,
    },
    "permanencia_prolongada": {
        "module": "core.outcomes.permanencia_prolongada",
        "class":  "PermanenciaProlongada",
        "name":   "Permanência Hospitalar Prolongada",
        "description": "Prediz internações com duração acima do percentil 90 para o mesmo grupo diagnóstico.",
        "data_sources": ["SIH"],
        "icon": "bed",
        "estimated_download_min": 10,
    },
    "infeccao_hospitalar": {
        "module": "core.outcomes.infeccao_hospitalar",
        "class":  "InfeccaoHospitalar",
        "name":   "Infecção Hospitalar",
        "description": "Prediz ocorrência de infecção adquirida durante a internação (CID T80-T88).",
        "data_sources": ["SIH"],
        "icon": "coronavirus",
        "estimated_download_min": 10,
    },
    "custo_elevado": {
        "module": "core.outcomes.custo_elevado",
        "class":  "CustoHospitalarElevado",
        "name":   "Custo Hospitalar Elevado",
        "description": "Prediz internações com custo acima do percentil 90 no mesmo grupo de procedimentos.",
        "data_sources": ["SIH"],
        "icon": "payments",
        "estimated_download_min": 10,
    },
    # Saúde Materno-Infantil
    "mortalidade_neonatal": {
        "module": "core.outcomes.mortalidade_neonatal",
        "class":  "MortalidadeNeonatal",
        "name":   "Mortalidade Neonatal",
        "description": "Prediz óbito neonatal (0-27 dias) linkando SINASC ao SIM.",
        "data_sources": ["SINASC", "SIM"],
        "icon": "child_care",
        "estimated_download_min": 12,
    },
    "baixo_peso_nascer": {
        "module": "core.outcomes.baixo_peso_nascer",
        "class":  "BaixoPesoNascer",
        "name":   "Baixo Peso ao Nascer",
        "description": "Prediz nascimentos com peso inferior a 2.500g a partir de dados do SINASC.",
        "data_sources": ["SINASC"],
        "icon": "scale",
        "estimated_download_min": 5,
    },
    "prematuridade": {
        "module": "core.outcomes.prematuridade",
        "class":  "Prematuridade",
        "name":   "Prematuridade",
        "description": "Prediz nascimentos com menos de 37 semanas de gestação.",
        "data_sources": ["SINASC"],
        "icon": "baby_changing_station",
        "estimated_download_min": 5,
    },
    "apgar_baixo": {
        "module": "core.outcomes.apgar_baixo",
        "class":  "ApgarBaixo",
        "name":   "Apgar Baixo no 5º Minuto",
        "description": "Prediz Apgar < 7 no 5º minuto, indicador de asfixia perinatal.",
        "data_sources": ["SINASC"],
        "icon": "cardiology",
        "estimated_download_min": 5,
    },
    # Tuberculose e Hanseníase
    "abandono_tb": {
        "module": "core.outcomes.abandono_tb",
        "class":  "AbandonoTB",
        "name":   "Abandono de Tratamento TB",
        "description": "Prediz abandono do tratamento de tuberculose antes da cura.",
        "data_sources": ["SINAN_TB"],
        "icon": "pulmonology",
        "estimated_download_min": 8,
    },
    "abandono_hanseniase": {
        "module": "core.outcomes.abandono_hanseniase",
        "class":  "AbandonoHanseniase",
        "name":   "Abandono de Tratamento — Hanseníase",
        "description": "Prediz abandono do tratamento de hanseníase antes da alta por cura.",
        "data_sources": ["SINAN_HANS"],
        "icon": "stethoscope",
        "estimated_download_min": 5,
    },
    # Arboviroses
    "dengue_grave": {
        "module": "core.outcomes.dengue_grave",
        "class":  "DengueGrave",
        "name":   "Dengue com Sinais de Alarme ou Grave",
        "description": "Prediz evolução para dengue grave ou com sinais de alarme no SINAN.",
        "data_sources": ["SINAN_DENG"],
        "icon": "pest_control",
        "estimated_download_min": 8,
    },
    "chikungunya_hospitalizado": {
        "module": "core.outcomes.chikungunya_hospitalizado",
        "class":  "ChikungunyaHospitalizado",
        "name":   "Hospitalização por Chikungunya",
        "description": "Prediz necessidade de hospitalização em casos notificados de chikungunya.",
        "data_sources": ["SINAN_CHIK"],
        "icon": "local_hospital",
        "estimated_download_min": 6,
    },
    # HIV e ISTs
    "obito_aids": {
        "module": "core.outcomes.obito_aids",
        "class":  "ObitoAIDS",
        "name":   "Óbito por AIDS",
        "description": "Prediz óbito em casos notificados de AIDS no SINAN.",
        "data_sources": ["SINAN_AIDS"],
        "icon": "medical_information",
        "estimated_download_min": 5,
    },
    "sifilis_nao_cura": {
        "module": "core.outcomes.sifilis_nao_cura",
        "class":  "SifilisNaoCura",
        "name":   "Não-Cura de Sífilis Adquirida",
        "description": "Prediz encerramento sem cura (abandono, óbito, transferência) em casos de sífilis.",
        "data_sources": ["SINAN_SIFA"],
        "icon": "medication",
        "estimated_download_min": 5,
    },
    # Violência e Intoxicações
    "violencia_autoprovocada": {
        "module": "core.outcomes.violencia_autoprovocada",
        "class":  "ViolenciaAutoprovocada",
        "name":   "Risco de Violência Autoprovocada / Suicídio",
        "description": "Prediz violência autoprovocada com base em notificações do SINAN.",
        "data_sources": ["SINAN_VIOL"],
        "icon": "psychology",
        "estimated_download_min": 10,
    },
    "intoxicacao_grave": {
        "module": "core.outcomes.intoxicacao_grave",
        "class":  "IntoxicacaoGrave",
        "name":   "Desfecho Adverso em Intoxicação Exógena",
        "description": "Prediz desfecho grave (óbito ou sequela) em intoxicações exógenas notificadas.",
        "data_sources": ["SINAN_IEXO"],
        "icon": "dangerous",
        "estimated_download_min": 10,
    },
}

OUTCOME_GROUPS: dict[str, list[str]] = {
    "Saúde Materno-Infantil": [
        "baixo_peso_nascer",
        "prematuridade",
        "apgar_baixo",
        "mortalidade_neonatal",
    ],
    "Internação Hospitalar": [
        "readmissao_30d",
        "permanencia_prolongada",
        "infeccao_hospitalar",
        "custo_elevado",
        "mortalidade_hospitalar",
    ],
    "Tuberculose e Hanseníase": [
        "abandono_tb",
        "abandono_hanseniase",
    ],
    "Arboviroses": [
        "dengue_grave",
        "chikungunya_hospitalizado",
    ],
    "HIV e ISTs": [
        "obito_aids",
        "sifilis_nao_cura",
    ],
    "Violência e Intoxicações": [
        "violencia_autoprovocada",
        "intoxicacao_grave",
    ],
}


# ── Lazy proxy ────────────────────────────────────────────────────────────────

class _LazyOutcome:
    """Holds metadata immediately; imports the real class only on first method call."""

    def __init__(self, key: str, meta: dict):
        self.key                   = key
        self.name                  = meta["name"]
        self.description           = meta["description"]
        self.data_sources          = meta["data_sources"]
        self.icon                  = meta.get("icon", "local_hospital")
        self.estimated_download_min = meta.get("estimated_download_min", 5)
        self._meta                 = meta
        self._instance             = None

    def _load(self):
        if self._instance is None:
            import importlib
            mod = importlib.import_module(self._meta["module"])
            self._instance = getattr(mod, self._meta["class"])()
        return self._instance

    def __getattr__(self, name: str):
        # Called for any attribute not found above (e.g. build_cohort, build_features)
        return getattr(self._load(), name)

    def __repr__(self):
        return f"<Outcome {self.key}>"


OUTCOMES: dict[str, _LazyOutcome] = {
    key: _LazyOutcome(key, meta)
    for key, meta in _REGISTRY.items()
}

# Keep OutcomeConfig importable from this package for type hints
from core.outcomes.base import OutcomeConfig  # noqa: E402
