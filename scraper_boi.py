import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO 

# URL alvo
url = "https://www.scotconsultoria.com.br/cotacoes/boi-gordo/"

def capturar_dados():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("Acessando o site...")
    resposta = requests.get(url, headers=headers)

   
    try:
        tabelas = pd.read_html(StringIO(resposta.text), decimal=',', thousands='.', match="Funrural")
        df = tabelas[1]
    except ValueError:
        raise Exception("Não encontrei a tabela contendo 'Funrural'. O layout do site mudou?")

    print(f"Tabela encontrada! Dimensões brutas: {df.shape}")

  
   
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0) 
        df.columns = df.columns.droplevel(0) 
    

    # 3. SELEÇÃO DE COLUNAS POR POSIÇÃO
    # Coluna 0: Nome da Praça (ex: SP Barretos)
    # Coluna 1: Preço à Vista Bruto
    # Coluna 2: Preço 30 Dias Bruto
    # Coluna 4: Variação (# base)
    df_limpo = df.iloc[:, [0, 1, 2, 4]].copy()
    df_limpo.columns = ['praca', 'preco_vista', 'preco_30d', 'variacao']
    # 4. FILTRAGEM DE SUJEIRA
    df_limpo['preco_vista'] = pd.to_numeric(df_limpo['preco_vista'], errors='coerce')
    df_limpo = df_limpo.dropna(subset=['preco_vista'])
    df_limpo['data_coleta'] = datetime.now().strftime("%Y-%m-%d")

    return df_limpo.to_dict(orient='records')

if __name__ == "__main__":
    try:
        dados = capturar_dados()
        with open('cotacoes_boi_hoje.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"\nSucesso Total! {len(dados)} linhas salvas.")
    except Exception as e:
        print(f"\nERRO: {e}")