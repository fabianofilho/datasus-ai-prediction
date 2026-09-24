"""Validação: HPO só no treino e Optuna semeado (PRED-08, ML-01, ML-10).

pages/analise.py é um script Streamlit e não roda fora do app, então a
ordem partição -> busca é conferida pela árvore sintática do arquivo. A
partição e a semente são testadas direto em core/models/pipeline.py.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core.models.pipeline import optimize_hyperparams, train_test_partition

ANALISE = Path(__file__).resolve().parent.parent / "pages" / "analise.py"
FUNCOES_HPO = {"optimize_hyperparams", "random_search", "grid_search"}


def _dados(n: int = 120, seed: int = 0) -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(seed)
    X = pd.DataFrame({"a": rng.normal(size=n), "b": rng.normal(size=n)})
    y = pd.Series((X["a"] + rng.normal(scale=0.5, size=n) > 0).astype(int))
    return X, y


# ── Partição ──────────────────────────────────────────────────────────────────

def test_holdout_disjunto_e_estratificado():
    X, y = _dados()
    X_tr, X_te, y_tr, y_te = train_test_partition(X, y, strategy="holdout", test_size=0.25)
    assert set(X_tr.index).isdisjoint(X_te.index)
    assert len(X_tr) + len(X_te) == len(X)
    assert len(X_te) == 30
    assert abs(y_tr.mean() - y_te.mean()) < 0.05


def test_temporal_treino_so_antes_do_corte():
    X, y = _dados(n=40)
    datas = pd.Series(pd.date_range("2020-01-01", periods=40, freq="D"))
    datas.iloc[3] = pd.NaT
    corte = "2020-01-31"
    X_tr, X_te, y_tr, y_te = train_test_partition(
        X, y, strategy="temporal", dates=datas, cutoff=corte,
    )
    d_tr = datas.iloc[X_tr.index]
    d_te = datas.iloc[X_te.index]
    assert (d_tr < pd.Timestamp(corte)).all()
    assert (d_te >= pd.Timestamp(corte)).all()
    # Linha sem data fica fora das duas partições.
    assert 3 not in X_tr.index and 3 not in X_te.index
    assert len(X_tr) == 29 and len(X_te) == 10
    assert len(y_tr) == len(X_tr) and len(y_te) == len(X_te)


def test_temporal_insuficiente_falha():
    X, y = _dados(n=20)
    datas = pd.Series(pd.date_range("2020-01-01", periods=20, freq="D"))
    with pytest.raises(ValueError, match="insuficiente"):
        train_test_partition(X, y, strategy="temporal", dates=datas, cutoff="2020-01-05")


def test_estrategia_desconhecida_falha():
    X, y = _dados()
    with pytest.raises(ValueError):
        train_test_partition(X, y, strategy="kfold")


# ── Optuna semeado ────────────────────────────────────────────────────────────

def test_optuna_com_mesma_semente_repete_os_hiperparametros():
    X, y = _dados()
    kw = dict(algorithm="logreg", n_trials=4, n_folds=3)
    a = optimize_hyperparams(X, y, seed=123, **kw)
    b = optimize_hyperparams(X, y, seed=123, **kw)
    assert a == b


def test_optuna_usa_tpe_com_a_semente(monkeypatch):
    import optuna

    sementes = []
    original = optuna.samplers.TPESampler

    class TPEEspiao(original):
        def __init__(self, *args, **kwargs):
            sementes.append(kwargs.get("seed"))
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(optuna.samplers, "TPESampler", TPEEspiao)
    X, y = _dados()
    optimize_hyperparams(X, y, algorithm="logreg", n_trials=1, n_folds=3, seed=7)
    assert sementes == [7]


# ── pages/analise.py: busca só na partição de treino ──────────────────────────

def _chamadas_hpo(arvore: ast.AST) -> list[ast.Call]:
    return [
        n for n in ast.walk(arvore)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FUNCOES_HPO
    ]


def test_analise_busca_hiperparametros_em_x_hpo():
    arvore = ast.parse(ANALISE.read_text(encoding="utf-8"))
    chamadas = _chamadas_hpo(arvore)
    assert {c.func.id for c in chamadas} == FUNCOES_HPO
    for c in chamadas:
        primeiro = c.args[0]
        assert isinstance(primeiro, ast.Name) and primeiro.id == "X_hpo", (
            f"{c.func.id} (linha {c.lineno}) precisa receber X_hpo, não {ast.unparse(primeiro)}"
        )
        assert ast.unparse(c.args[1]) == "y_hpo"


def test_analise_particiona_antes_da_busca():
    arvore = ast.parse(ANALISE.read_text(encoding="utf-8"))
    particoes = [
        n.lineno for n in ast.walk(arvore)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == "train_test_partition"
    ]
    estrategias = {
        kw.value.value
        for n in ast.walk(arvore)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == "train_test_partition"
        for kw in n.keywords if kw.arg == "strategy"
    }
    assert estrategias == {"holdout", "temporal"}
    primeira_busca = min(c.lineno for c in _chamadas_hpo(arvore))
    assert particoes and max(particoes) < primeira_busca
    # O holdout não pode mais ser sorteado depois da busca.
    splits_depois = [
        n.lineno for n in ast.walk(arvore)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        and n.func.id == "train_test_split" and n.lineno > primeira_busca
    ]
    assert not splits_depois


def test_analise_passa_semente_da_tela_ao_optuna():
    arvore = ast.parse(ANALISE.read_text(encoding="utf-8"))
    optuna_calls = [c for c in _chamadas_hpo(arvore) if c.func.id == "optimize_hyperparams"]
    assert optuna_calls
    for c in optuna_calls:
        seeds = [kw for kw in c.keywords if kw.arg == "seed"]
        assert seeds and ast.unparse(seeds[0].value) == "_hpo_seed"
    assert 'int(ss.get("sample_seed", 42))' in ANALISE.read_text(encoding="utf-8").replace("'", '"')


# ── Balanceamento padrão (ML-02) ──────────────────────────────────────────────

def test_balanceamento_padrao_e_nenhum():
    # Class Weight não faz nada em XGBoost e MLP e piora a calibração nos
    # demais; o padrão da tela é não balancear.
    arvore = ast.parse(ANALISE.read_text(encoding="utf-8"))
    radios = [
        n for n in ast.walk(arvore)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "radio" and n.args
        and isinstance(n.args[0], ast.Constant) and n.args[0].value == "Balanceamento"
    ]
    assert len(radios) == 1
    radio = radios[0]
    opcoes = ast.literal_eval(radio.args[1])
    indice = next((kw.value.value for kw in radio.keywords if kw.arg == "index"), 0)
    assert opcoes[indice] == "Nenhum"
