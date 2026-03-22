from core.outcomes.base import OutcomeConfig

# Internação hospitalar (SIH)
from core.outcomes.mortalidade_hospitalar import MortalidadeHospitalar
from core.outcomes.readmissao_30d import ReadmissaoHospitalar30d
from core.outcomes.permanencia_prolongada import PermanenciaProlongada
from core.outcomes.infeccao_hospitalar import InfeccaoHospitalar
from core.outcomes.custo_elevado import CustoHospitalarElevado

# Saúde materno-infantil (SINASC + SIM)
from core.outcomes.mortalidade_neonatal import MortalidadeNeonatal
from core.outcomes.baixo_peso_nascer import BaixoPesoNascer
from core.outcomes.prematuridade import Prematuridade
from core.outcomes.apgar_baixo import ApgarBaixo

# Tuberculose e Hanseníase (SINAN)
from core.outcomes.abandono_tb import AbandonoTB
from core.outcomes.abandono_hanseniase import AbandonoHanseniase

# Arboviroses (SINAN)
from core.outcomes.dengue_grave import DengueGrave
from core.outcomes.chikungunya_hospitalizado import ChikungunyaHospitalizado

# HIV e ISTs (SINAN)
from core.outcomes.obito_aids import ObitoAIDS
from core.outcomes.sifilis_nao_cura import SifilisNaoCura

# Violência e Intoxicações (SINAN)
from core.outcomes.violencia_autoprovocada import ViolenciaAutoprovocada
from core.outcomes.intoxicacao_grave import IntoxicacaoGrave

# ── Agrupamento por tópico para exibição na UI ─────────────────────────────
OUTCOME_GROUPS: dict[str, list[str]] = {
    "Internação Hospitalar": [
        "mortalidade_hospitalar",
        "readmissao_30d",
        "permanencia_prolongada",
        "infeccao_hospitalar",
        "custo_elevado",
    ],
    "Saúde Materno-Infantil": [
        "mortalidade_neonatal",
        "baixo_peso_nascer",
        "prematuridade",
        "apgar_baixo",
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

OUTCOMES: dict[str, OutcomeConfig] = {
    o.key: o
    for o in [
        MortalidadeHospitalar(),
        ReadmissaoHospitalar30d(),
        PermanenciaProlongada(),
        InfeccaoHospitalar(),
        CustoHospitalarElevado(),
        MortalidadeNeonatal(),
        BaixoPesoNascer(),
        Prematuridade(),
        ApgarBaixo(),
        AbandonoTB(),
        AbandonoHanseniase(),
        DengueGrave(),
        ChikungunyaHospitalizado(),
        ObitoAIDS(),
        SifilisNaoCura(),
        ViolenciaAutoprovocada(),
        IntoxicacaoGrave(),
    ]
}
