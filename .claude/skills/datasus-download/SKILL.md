# Skill: Download de Dados DATASUS — datasus-ai-prediction

Referência para entender, depurar ou estender o sistema de download.

**Arquivo central:** `core/data/downloader.py`

---

## Estratégia em cascata (ordem de tentativa)

```
1. Cache parquet local
   RAW_DIR/{fonte}_{uf}_{ano}.parquet
   (RAW_DIR = "data/raw/" local | "/tmp/datasus_raw" no Streamlit Cloud)

2. HTTP Mirror (DigitalOcean CDN)
   https://datasus-ftp-mirror.nyc3.cdn.digitaloceanspaces.com/{path}
   → Mesmo espelho do FTP, sem autenticação, mais rápido

3. FTP oficial
   ftp.datasus.gov.br (modo passivo)

4. Upload manual
   Streamlit file_uploader — usuário exporta CSV pelo TABNET
```

---

## Padrões de arquivo por sistema

| Sistema    | Padrão de arquivo             | Frequência | Filtro   |
|------------|-------------------------------|------------|----------|
| SIH        | `RD{UF}{aa}{mm}.dbc`          | Mensal     | Por UF   |
| SIM        | `DO{UF}{aaaa}.dbc`            | Anual      | Por UF   |
| SINASC     | `DN{UF}{aaaa}.dbc`            | Anual      | Por UF   |
| SINAN_TB   | `TUBEBR{aa}.dbc`              | Anual      | Nacional (filtrado por UF_SG_NOT) |
| SINAN_HANS | `HANSBR{aa}.dbc`              | Anual      | Nacional |
| SINAN_DENG | `DENGBR{aa}.dbc`              | Anual      | Nacional |
| SINAN_CHIK | `CHIKBR{aa}.dbc`              | Anual      | Nacional |
| SINAN_AIDS | `AIDABR{aa}.dbc`              | Anual      | Nacional |
| SINAN_SIFA | `SIFABR{aa}.dbc`              | Anual      | Nacional |
| SINAN_VIOL | `VIOLBR{aa}.dbc`              | Anual      | Nacional |
| SINAN_IEXO | `IEXOBR{aa}.dbc`              | Anual      | Nacional |

Onde: `{UF}` = sigla (ex: SP, RJ), `{aa}` = ano 2 dígitos, `{aaaa}` = ano 4 dígitos, `{mm}` = mês 2 dígitos.

---

## Descompressão DBC

Biblioteca: `datasus-dbc` (puro Python, sem compilador C).

```python
from datasus_dbc import read_dbc
df = read_dbc("arquivo.dbc")   # retorna pandas DataFrame
```

Alternativa para cache: `dbc_to_parquet("arquivo.dbc", "saida.parquet")`.

**Não usar** `pySUS` / `pyreaddbc` — requerem compilador C e falham no Streamlit Cloud.

---

## Códigos dos estados (27 UFs)

```python
STATES = [
    "AC","AL","AM","AP","BA","CE","DF","ES","GO",
    "MA","MG","MS","MT","PA","PB","PE","PI","PR",
    "RJ","RN","RO","RR","RS","SC","SE","SP","TO"
]
```

Mapeamento IBGE (código numérico → sigla):
```python
IBGE_TO_UF = {
    11:"RO", 12:"AC", 13:"AM", 14:"RR", 15:"PA", 16:"AP", 17:"TO",
    21:"MA", 22:"PI", 23:"CE", 24:"RN", 25:"PB", 26:"PE", 27:"AL",
    28:"SE", 29:"BA", 31:"MG", 32:"ES", 33:"RJ", 35:"SP", 41:"PR",
    42:"SC", 43:"RS", 50:"MS", 51:"MT", 52:"GO", 53:"DF"
}
```

---

## Sentinel values DATASUS

Valores que significam "ignorado/desconhecido" e devem ser tratados como `NaN`:

| Valor | Significado                        |
|-------|------------------------------------|
| `9`   | Ignorado (campos com 1 dígito)     |
| `99`  | Ignorado (campos com 2 dígitos)    |
| `999` | Ignorado (campos com 3 dígitos)    |

O `SentinelReplacer` no pipeline substitui 9 e 99 por `NaN` automaticamente. Nas funções de pré-processamento (`core/data/*.py`), outros valores especiais são tratados caso a caso (ex: IDADE no SIM usa prefixo para indicar unidade).

---

## Lógica de cache parquet

```python
cache_path = RAW_DIR / f"{source}_{uf}_{year}.parquet"
if cache_path.exists():
    return pd.read_parquet(cache_path)
# ... download ...
df.to_parquet(cache_path, index=False)
```

Para forçar re-download: deletar o `.parquet` correspondente em `data/raw/`.

---

## Pré-processadores por sistema

| Sistema  | Módulo                  | Função principal   | Notas                              |
|----------|-------------------------|--------------------|-------------------------------------|
| SIH      | `core.data.sih`         | `preprocess(df)`   | Extrai 23 colunas, calcula LOS      |
| SIM      | `core.data.sim`         | `preprocess(df)`   | Decodifica campo IDADE (prefixo)    |
| SINASC   | `core.data.sinasc`      | `preprocess(df)`   | Deriva preterm, low_birth_weight   |
| SINAN_TB | `core.data.sinan`       | `preprocess(df)`   | Filtra casos encerrados, decodifica NU_IDADE_N |
| Outros   | `core.data.sinan_*`     | `preprocess(df)`   | Específico por doença               |

---

## Adicionando nova fonte de dados

1. Adicionar entrada em `FTP_CONFIG` em `core/data/downloader.py` com padrão de arquivo e caminho FTP
2. Criar `core/data/{nova_fonte}.py` com função `preprocess(df) -> pd.DataFrame`
3. Referenciar a nova fonte em `data_sources` do OutcomeConfig correspondente
