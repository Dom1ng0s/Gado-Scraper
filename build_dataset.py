import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def git_commits_for_file(filename: str) -> list[tuple[str, str]]:
    """Returns [(hash, YYYY-MM-DD), ...] for every commit that touched filename."""
    result = subprocess.run(
        ["git", "log", "--format=%H %ad", "--date=short", "--", filename],
        capture_output=True,
        text=True,
        check=True,
    )
    commits = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            commits.append((parts[0], parts[1]))
    return commits


def file_at_commit(commit_hash: str, filename: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit_hash}:{filename}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def build_dataframe(filename: str) -> pd.DataFrame:
    commits = git_commits_for_file(filename)
    print(f"\n{filename}: {len(commits)} commits encontrados")

    frames = []
    skipped = 0

    for commit_hash, commit_date in commits:
        try:
            raw = file_at_commit(commit_hash, filename)
            records = json.loads(raw)
            if not isinstance(records, list) or len(records) == 0:
                raise ValueError("JSON vazio ou formato inesperado")
            df = pd.DataFrame(records)
            df["data"] = commit_date
            frames.append(df)
        except Exception as e:
            print(f"  [SKIP] {commit_hash[:8]} ({commit_date}): {e}", file=sys.stderr)
            skipped += 1

    if skipped:
        print(f"  {skipped} commit(s) ignorado(s) por erro")

    if not frames:
        raise RuntimeError(f"Nenhum dado válido encontrado para {filename}")

    combined = pd.concat(frames, ignore_index=True)

    # Usa a data do commit como coluna canônica; remove a data_coleta do JSON se existir
    combined["data"] = pd.to_datetime(combined["data"]).dt.date
    combined = combined.drop(columns=["data_coleta"], errors="ignore")

    # Garante tipos numéricos (histórico antigo pode ter strings)
    for col in ["preco_vista", "preco_30d", "variacao"]:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")

    return combined.sort_values("data").reset_index(drop=True)


def print_summary(name: str, df: pd.DataFrame) -> None:
    print(f"\n{'=' * 50}")
    print(f"Resumo — {name}")
    print(f"  Dias coletados : {df['data'].nunique()}")
    print(f"  Período        : {df['data'].min()} → {df['data'].max()}")
    print(f"  Praças         : {sorted(df['praca'].unique())}")
    print(f"  Total de linhas: {len(df)}")


def main() -> None:
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    datasets = [
        ("cotacoes_boi_hoje.json", "historico_boi", "Boi Gordo"),
        ("cotacoes_novilha_hoje.json", "historico_novilha", "Novilha"),
    ]

    for filename, stem, label in datasets:
        df = build_dataframe(filename)
        out_path = output_dir / f"{stem}.csv"
        df.to_csv(out_path, index=False)
        print(f"  Salvo: {out_path}")
        print_summary(label, df)


if __name__ == "__main__":
    main()
