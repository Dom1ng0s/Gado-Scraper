# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated ETL pipeline that scrapes daily cattle market prices from [scotconsultoria.com.br](https://www.scotconsultoria.com.br) and commits them as JSON to the repository. **Git itself is the historical database** — every daily commit is a queryable snapshot of market data.

## Running the Scrapers

```bash
# Install dependencies
pip install -r requirements.txt

# Run individually
python scraper_boi.py      # → cotacoes_boi_hoje.json
python scraper_novilha.py  # → cotacoes_novilha_hoje.json
```

There are no tests. Validation is done by checking the script output: success prints `Sucesso Total! N linhas salvas.`; failure prints `ERRO: <message>`.

## Architecture

Both scrapers follow the same pattern:
1. `requests.get` with a browser User-Agent to fetch the page
2. `pd.read_html(..., match="Funrural")` to locate the price table (the `"Funrural"` string is the stable anchor — if scraping breaks, this is the first thing to check)
3. MultiIndex header flattening (two `droplevel(0)` calls)
4. Column selection by position (not by name, since headers change)
5. JSON dump to the repo root

**`scraper_boi.py`** targets `tabelas[1]` and extracts 4 columns: `praca`, `preco_vista`, `preco_30d`, `variacao`.  
**`scraper_novilha.py`** targets `tabelas[0]` and extracts 3 columns: `praca`, `preco_vista`, `preco_30d` (no `variacao`).

## Automation (GitHub Actions)

`.github/workflows/atualizacao_diaria.yml` runs both scrapers and auto-commits the JSONs:
- **Scheduled:** daily at 09:00 UTC
- **On push to `main`:** also triggers (useful for testing workflow changes)
- **Manual:** via `workflow_dispatch`

The workflow only commits when files actually changed (`git diff --staged --quiet` guard). Requires `contents: write` permission — this must be enabled in the fork's Settings → Actions → General.

## Output Format

```json
[
  {
    "praca": "SP Barretos",
    "preco_vista": 320.50,
    "preco_30d": 322.00,
    "variacao": 1.5,         // boi only
    "data_coleta": "2026-06-07"
  }
]
```

## Querying Historical Data

Since data lives in git, historical prices can be retrieved with:
```bash
git show <commit-hash>:cotacoes_boi_hoje.json
git log --oneline  # each commit = one day of data
```
