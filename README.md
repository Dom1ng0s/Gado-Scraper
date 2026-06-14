# 🐄 Gado-Scraper

**Pipeline ETL automatizada para monitoramento diário de cotações pecuárias brasileiras**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automatizado-2088FF?style=flat&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Pipeline-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Praças](https://img.shields.io/badge/Praças_Monitoradas-33-green?style=flat)](https://github.com/Dom1ng0s/Gado-Scraper)
[![License](https://img.shields.io/badge/License-MIT-brightgreen?style=flat)](LICENSE)
![Última atualização](https://img.shields.io/github/last-commit/Dom1ng0s/Gado-Scraper?label=última%20atualização)

Pipeline de dados que coleta e agrega automaticamente as cotações de **boi gordo** e **novilha** de 33 praças pecuárias do Brasil todos os dias. O sistema roda 100% na nuvem via GitHub Actions — sem servidores, sem custo de infraestrutura e sem intervenção manual. Os dados gerados alimentam diretamente o [Sistema de Gestão de Gado](https://sistemadogado.up.railway.app).

---

## Índice

1. [O Problema que Este Projeto Resolve](#-o-problema-que-este-projeto-resolve)
2. [Funcionalidades](#-funcionalidades)
3. [Arquitetura](#-arquitetura)
4. [Requisitos](#-requisitos)
5. [Instalação e Execução](#-instalação-e-execução)
6. [Como Usar](#-como-usar)
7. [Formato dos Dados](#-formato-dos-dados)
8. [O que Foi Feito](#-o-que-foi-feito)
9. [Próximas Evoluções](#-próximas-evoluções)
10. [Licença](#-licença)

---

## 💡 O Problema que Este Projeto Resolve

Pecuaristas tomam decisões de compra e venda com base nas cotações do dia, mas essas informações estão espalhadas em dezenas de sites de difícil acesso — e não existem APIs públicas confiáveis para o setor.

O Gado-Scraper resolve isso com uma arquitetura de **custo zero**:

- **GitHub Actions como cron job** — dispara o scraper diariamente às 09:00 UTC no fechamento do mercado
- **Git como banco de dados histórico** — cada commit diário é um snapshot de dados pronto para análise de séries temporais
- **CSV acumulativo** — histórico completo acessível em `data/` sem precisar parsear o git
- **Alertas via Telegram** — notificação de sucesso diário e alerta imediato em caso de falha

---

## ✨ Funcionalidades

Extraídas diretamente do código:

- Scraping das cotações de **boi gordo** (`scraper_boi.py`) e **novilha** (`scraper_novilha.py`) com âncora estável na string `"Funrural"` — se o layout do site mudar, este é o primeiro ponto a verificar
- **Retry automático** com 3 tentativas e backoff de 5 segundos entre elas; timeout de 15 segundos por requisição
- **Deduplicação por `(data, praça)`** em `append_historico.py` — evita registros duplicados se o pipeline rodar mais de uma vez no mesmo dia
- **Reconstrução completa do histórico** via `build_dataset.py` — percorre todo o `git log` e reconstrói os CSVs a partir dos commits (útil após um fork)
- **Notificações Telegram** configuráveis via secrets: sucesso diário e alertas de falha com link direto para o log do Actions
- **EDA completa** em `notebooks/01_eda.ipynb` com análise temporal, regional, correlação entre praças e comparativo boi × novilha

---

## 🏗️ Arquitetura

### Fluxo ETL

```
GitHub Actions (cron 09:00 UTC)
        │
        ├─► scraper_boi.py ──────┐
        │   (scotconsultoria.com) │
        │                        ▼
        │                cotacoes_boi_hoje.json
        │                        │
        ├─► scraper_novilha.py ──┤
        │   (scotconsultoria.com) │
        │                        ▼
        │             cotacoes_novilha_hoje.json
        │                        │
        └─► append_historico.py ─┘
                │
                ├─► data/historico_boi.csv     (acumulativo)
                └─► data/historico_novilha.csv (acumulativo)
                        │
                        ▼
              git commit "Dados atualizados: YYYY-MM-DD"
                        │
                        ▼
              Telegram: ✅ sucesso ou ❌ falha
```

### Git como Banco de Dados Histórico

Em vez de um banco de dados tradicional, cada commit diário funciona como um registro imutável e versionado. Isso elimina custo de infraestrutura e torna o histórico auditável:

```bash
# Consultar cotações de uma data específica
git show <commit-hash>:cotacoes_boi_hoje.json

# Ver todo o histórico de commits (um por dia)
git log --oneline
```

O `build_dataset.py` automatiza essa consulta: itera sobre todos os commits que tocaram os JSONs e reconstrói os CSVs com tipagem correta, removendo duplicatas e normalizando colunas numéricas.

### Lógica de Scraping (`scraper/base.py`)

| Etapa | Detalhe |
|---|---|
| Fetch | `requests.get` com User-Agent de browser para evitar bloqueio |
| Parse | `pd.read_html(match="Funrural")` — âncora estável na tabela |
| Flatten | `droplevel(0)` recursivo para achatar MultiIndex |
| Select | Colunas por posição (`COLUNAS_IDX`), não por nome — robusto a mudanças de header |
| Output | JSON com `data_coleta` no formato `YYYY-MM-DD` |

---

## 📋 Requisitos

- Python 3.9+
- Dependências (instaladas via `pip`):

```
pandas, requests, lxml, openpyxl
matplotlib, seaborn, scipy, numpy
jupyter, nbconvert
```

---

## 🚀 Instalação e Execução

### Rodar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/Dom1ng0s/Gado-Scraper.git
cd Gado-Scraper

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute os scrapers
python scraper_boi.py       # → cotacoes_boi_hoje.json
python scraper_novilha.py   # → cotacoes_novilha_hoje.json
python append_historico.py  # → atualiza data/historico_*.csv
```

**Saída esperada:**
```
Acessando o site... (tentativa 1/3)
Tabela encontrada! Dimensões brutas: (35, 8)
Sucesso Total! 33 linhas salvas em 'cotacoes_boi_hoje.json'.
```

### Usar em Seu Próprio Fork (Pipeline Automática)

A pipeline é 100% autossuficiente em qualquer fork:

1. Faça o fork deste repositório
2. Vá em **Settings → Actions → General** e habilite `Read and write permissions`
3. *(Opcional)* Para alertas Telegram, adicione em **Settings → Secrets and variables → Actions**:
   - `TELEGRAM_TOKEN` — token do seu bot (obtenha via [@BotFather](https://t.me/botfather))
   - `TELEGRAM_CHAT_ID` — ID do chat (descubra via [@userinfobot](https://t.me/userinfobot))
4. O GitHub Actions passará a rodar automaticamente todos os dias às 09:00 UTC

---

## 📖 Como Usar

### Reconstruir o Histórico Completo

Se você fez um fork e quer reconstruir os CSVs a partir do zero com base nos commits:

```bash
python build_dataset.py
```

O script percorre todo o `git log` e gera `data/historico_boi.csv` e `data/historico_novilha.csv` com todos os dados históricos, ignorando commits com JSON malformado.

### Análise Exploratória (EDA)

```bash
jupyter notebook notebooks/01_eda.ipynb
```

O notebook cobre: diagnóstico de qualidade, limpeza, ranking de praças por preço médio e volatilidade, evolução temporal, agrupamento regional e correlação entre praças.

---

## 📊 Formato dos Dados

### JSON do Dia

```json
[
  {
    "praca": "SP Barretos",
    "preco_vista": 320.50,
    "preco_30d": 322.00,
    "variacao": 1.5,
    "data_coleta": "2026-06-14"
  }
]
```

> **Nota:** `variacao` existe apenas em `cotacoes_boi_hoje.json`; o scraper de novilha não coleta essa coluna.

### CSV Histórico (`data/historico_boi.csv`)

```
praca,preco_vista,preco_30d,variacao,data
SP Barretos,320.5,322.0,1.5,2026-06-14
MS Campo Grande,315.0,316.5,0.8,2026-06-14
...
```

---

## ✅ O que Foi Feito

- Integração direta com o `sistema_gado` para alimentar cotações em tempo real
- Exportação automatizada para CSV (`data/historico_boi.csv`, `data/historico_novilha.csv`)
- Notificações via Telegram (sucesso diário e alertas de falha com link para o log)
- EDA completa do histórico com análise temporal, regional e correlação entre praças

---

## 🗺️ Próximas Evoluções

- [ ] Dashboard interativo com histórico de variações de preço (Streamlit ou Grafana)
- [ ] Alerta automático quando o preço em uma praça-chave ultrapassar um threshold configurável

---

## 👤 Autor

**Davi Domingos de Oliveira**
Estudante de Ciência da Computação — UFAL | Backend Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/davidomingosdeoliveira/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/Dom1ng0s)
[![Email](https://img.shields.io/badge/Email-D14836?style=flat&logo=gmail&logoColor=white)](mailto:odomingosdavi@gmail.com)

---

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.
