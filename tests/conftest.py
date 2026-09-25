"""Configuração comum dos testes: põe a raiz do repositório no sys.path.

O app roda com `streamlit run app.py` a partir da raiz, então os módulos
são importados como `core.*`. Os testes seguem a mesma convenção.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
