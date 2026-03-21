from core.outcomes.base import OutcomeConfig
from core.outcomes.readmissao_30d import ReadmissaoHospitalar30d
from core.outcomes.mortalidade_hospitalar import MortalidadeHospitalar
from core.outcomes.mortalidade_neonatal import MortalidadeNeonatal
from core.outcomes.abandono_tb import AbandonoTB

OUTCOMES: dict[str, OutcomeConfig] = {
    o.key: o
    for o in [
        ReadmissaoHospitalar30d(),
        MortalidadeHospitalar(),
        MortalidadeNeonatal(),
        AbandonoTB(),
    ]
}
