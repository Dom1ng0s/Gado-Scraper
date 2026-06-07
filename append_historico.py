import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

DATASETS = [
    ("cotacoes_boi_hoje.json", "data/historico_boi.csv"),
    ("cotacoes_novilha_hoje.json", "data/historico_novilha.csv"),
]


def append(json_path: str, csv_path: str, hoje: str) -> None:
    json_file = Path(json_path)
    csv_file = Path(csv_path)

    if not json_file.exists():
        raise FileNotFoundError(f"JSON do dia não encontrado: {json_path}")

    novos = pd.DataFrame(json.loads(json_file.read_text(encoding="utf-8")))
    novos["data"] = hoje
    novos = novos.drop(columns=["data_coleta"], errors="ignore")

    if csv_file.exists():
        historico = pd.read_csv(csv_file, dtype=str)
        if hoje in historico["data"].values:
            print(f"  {csv_path}: data {hoje} já registrada, nada a fazer.")
            return
        atualizado = pd.concat([historico, novos], ignore_index=True)
    else:
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        atualizado = novos

    atualizado.to_csv(csv_file, index=False)
    print(f"  {csv_path}: +{len(novos)} registros adicionados ({hoje}).")


def main() -> None:
    hoje = str(date.today())
    erros = []
    for json_path, csv_path in DATASETS:
        try:
            append(json_path, csv_path, hoje)
        except Exception as e:
            print(f"ERRO em {json_path}: {e}", file=sys.stderr)
            erros.append(json_path)

    if erros:
        sys.exit(1)


if __name__ == "__main__":
    main()
