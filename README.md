# 🐂 Gado-Scraper: Automação de Cotações Pecuárias

> **Pipeline automatizada para coleta e monitoramento diário de preços do boi gordo e novilha.**

Este projeto utiliza Web Scraping para extrair cotações atualizadas do setor pecuário e armazena os dados em formato JSON. O diferencial é a automação total via **GitHub Actions**, que executa o script diariamente, garantindo dados sempre frescos sem intervenção manual.

## 🚀 Funcionalidades

- **🐍 Scraping Inteligente:** Scripts em Python especializados para extrair dados de fontes do setor.
- **🤖 Automação Total:** Workflow do GitHub Actions configurado para rodar todos os dias.
- **📊 Dados Estruturados:** Exportação automática para arquivos `.json` (`cotacoes_boi_hoje.json` e `cotacoes_novilha_hoje.json`).
- **🔄 Histórico de Commits:** O próprio repositório serve como um log histórico das variações de preço.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Bibliotecas:** `requests`, `beautifulsoup4`
- **CI/CD:** GitHub Actions (Agendamento via Cron)

## 📂 Estrutura de Dados

Os dados coletados seguem o formato:
```json
{
  "data": "2026-01-15",
  "preco": "R$ XXX,XX",
  "regiao": "..."
}
```

## ⚙️ Como Funciona a Automação

O arquivo `.github/workflows/atualizacao_diaria.yml` está configurado para:
1. Instalar o ambiente Python.
2. Executar os scripts `scraper_boi.py` e `scraper_novilha.py`.
3. Realizar o `git commit` e `push` dos arquivos JSON atualizados de volta para o repositório.

## 💻 Como Executar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/Dom1ng0s/Gado-Scraper.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o scraper:
   ```bash
   python scraper_boi.py
   ```

---
Desenvolvido por [Davi Domingos](https://github.com/Dom1ng0s)
