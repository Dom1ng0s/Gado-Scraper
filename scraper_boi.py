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

    # 1. ESTRATÉGIA DE BUSCA
    # O parametro 'match' faz o pandas procurar uma tabela que tenha a palavra "Funrural" dentro.
    # Isso garante que pegamos a tabela da imagem, e não outra aleatória.
    try:
        tabelas = pd.read_html(StringIO(resposta.text), decimal=',', thousands='.', match="Funrural")
        df = tabelas[1]
    except ValueError:
        raise Exception("Não encontrei a tabela contendo 'Funrural'. O layout do site mudou?")

    print(f"Tabela encontrada! Dimensões brutas: {df.shape}")

    # 2. LIMPEZA DOS CABEÇALHOS (O pulo do gato)
    # Como a tabela tem 3 linhas de cabeçalho mesclado, o Pandas cria uma tupla complexa.
    # Vamos simplificar: jogar fora o cabeçalho atual e pegar os dados brutos.
    
    # Se o cabeçalho for MultiIndex (várias linhas), vamos achatá-lo
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0) # Remove "Boi Gordo/Preços Brutos"
        df.columns = df.columns.droplevel(0) # Remove "Funrural/Senar"
        # Agora deve sobrar algo como: ["Praça", "à vista", "30 d", "#", ...]

    # 3. SELEÇÃO DE COLUNAS POR POSIÇÃO (Olhando sua imagem)
    # Coluna 0: Nome da Praça (ex: SP Barretos)
    # Coluna 1: Preço à Vista Bruto
    # Coluna 2: Preço 30 Dias Bruto
    # Coluna 3: Geralmente é o ícone colorido (pode vir vazio ou sujo)
    # Coluna 4: Variação (# base)
    
    # Vamos pegar as colunas 0, 1, 2 e 4
    df_limpo = df.iloc[:, [0, 1, 2, 4]].copy()
    
    # Renomear para facilitar
    df_limpo.columns = ['praca', 'preco_vista', 'preco_30d', 'variacao']

    # 4. FILTRAGEM DE SUJEIRA
    # Às vezes o cabeçalho se repete no meio dos dados. Vamos remover linhas onde o preço não é número.
    # "Coerce" transforma o que não for número em NaN (Not a Number) para podermos apagar.
    df_limpo['preco_vista'] = pd.to_numeric(df_limpo['preco_vista'], errors='coerce')
    df_limpo = df_limpo.dropna(subset=['preco_vista'])

    # Adiciona data
    df_limpo['data_coleta'] = datetime.now().strftime("%Y-%m-%d")

    # Debug: Mostra as primeiras linhas para você ver se deu certo
    print("\n--- Amostra dos Dados ---")
    print(df_limpo.head())
    
    return df_limpo.to_dict(orient='records')

if __name__ == "__main__":
    try:
        dados = capturar_dados()
        with open('cotacoes_boi_hoje.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print(f"\nSucesso Total! {len(dados)} linhas salvas.")
    except Exception as e:
        print(f"\nERRO: {e}")