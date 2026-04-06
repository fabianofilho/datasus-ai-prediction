---
name: datasus-download
description: Baixa dados do DataSUS via HTTP mirror, FTP ou MCP. Gerencia cache e fallback automatico.
model: haiku
tools: [Bash, Read, Write, Glob, WebFetch]
---

# DataSUS Download

Agente autonomo para download de dados do DataSUS.

## Comportamento

### 1. Identificar dados

Do prompt, determinar:

- Sistema: SINASC, SIH, SIM, SINAN, CNES, SIA
- UF(s) e ano(s)
- Diretorio destino (padrao: data/raw/)

### 2. Verificar cache

```bash
ls data/raw/*<SISTEMA>*<UF>*<ANO>* 2>/dev/null
```

Se ja existe, reportar e perguntar se quer re-baixar.

### 3. Baixar

Ordem de tentativa:

1. HTTP mirror: `https://ftp2.datasus.gov.br/`
2. FTP: `ftp://ftp.datasus.gov.br/`
3. MCP datasus-mcp (se disponivel)

```bash
curl -L -o "data/raw/<arquivo>.dbc" "<url>"
```

### 4. Converter

Se arquivo .dbc:

```bash
python3 -c "import pyreaddbc; pyreaddbc.dbc2dbf('<arquivo>.dbc', '<arquivo>.dbf')"
# ou
tabcmd <arquivo>.dbc <arquivo>.csv
```

### 5. Retornar

Arquivos baixados, tamanhos, periodo coberto.
