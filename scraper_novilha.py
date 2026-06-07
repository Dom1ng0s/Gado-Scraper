import sys
from scraper.base import capturar_cotacoes

URL = "https://www.scotconsultoria.com.br/cotacoes/novilha/?ref=smn"
COLUNAS_IDX = [0, 1, 2]
COLUNAS_NOMES = ["praca", "preco_vista", "preco_30d"]

if __name__ == "__main__":
    try:
        capturar_cotacoes(URL, 0, COLUNAS_IDX, COLUNAS_NOMES, "cotacoes_novilha_hoje.json")
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)
