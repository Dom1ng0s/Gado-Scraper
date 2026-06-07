import json
import sys
import time
from datetime import datetime
from io import StringIO

import pandas as pd
import requests

try:
    from notificador import send_alert
except ImportError:
    def send_alert(msg: str) -> None:  # type: ignore[misc]
        print(f"[notificador indisponível] {msg}", file=sys.stderr)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
_TIMEOUT = 15
_RETRIES = 3
_BACKOFF = 5


def capturar_cotacoes(
    url: str,
    tabela_idx: int,
    colunas_idx: list[int],
    colunas_nomes: list[str],
    output_path: str,
    match: str = "Funrural",
) -> None:
    html = _fetch_with_retry(url)
    tabelas = _parse_table(html, match)
    df = _clean(tabelas[tabela_idx], colunas_idx, colunas_nomes)

    records = df.to_dict(orient="records")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    print(f"Sucesso Total! {len(records)} linhas salvas em '{output_path}'.")


def _fetch_with_retry(url: str) -> str:
    last_exc: Exception = RuntimeError("Sem tentativas")
    for attempt in range(1, _RETRIES + 1):
        try:
            print(f"Acessando o site... (tentativa {attempt}/{_RETRIES})")
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            last_exc = e
            print(f"  Falha: {e}")
            if attempt < _RETRIES:
                time.sleep(_BACKOFF)
    msg = f"Todas as {_RETRIES} tentativas falharam: {last_exc}"
    send_alert(f"❌ *Gado-Scraper* — falha de rede ao acessar:\n`{url}`\n\n{msg}")
    raise RuntimeError(msg) from last_exc


def _parse_table(html: str, match: str) -> list[pd.DataFrame]:
    try:
        return pd.read_html(StringIO(html), decimal=",", thousands=".", match=match)
    except ValueError:
        raise RuntimeError(
            f"Tabela com '{match}' não encontrada. O layout do site mudou?"
        )


def _clean(df: pd.DataFrame, colunas_idx: list[int], colunas_nomes: list[str]) -> pd.DataFrame:
    # Flatten MultiIndex defensively: drop levels enquanto houver mais de um
    while isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels > 1:
        df.columns = df.columns.droplevel(0)

    print(f"Tabela encontrada! Dimensões brutas: {df.shape}")

    df = df.iloc[:, colunas_idx].copy()
    df.columns = colunas_nomes

    df["preco_vista"] = pd.to_numeric(df["preco_vista"], errors="coerce")
    df = df.dropna(subset=["preco_vista"])
    df["data_coleta"] = datetime.now().strftime("%Y-%m-%d")
    return df
