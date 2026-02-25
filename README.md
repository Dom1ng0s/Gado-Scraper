<div align="center">

# 🚜 Gado-Scraper

**Pipeline automatizada para monitoramento diário de cotações pecuárias**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-Scraping-4B8BBE?style=for-the-badge)](https://pypi.org/project/beautifulsoup4/)
[![Status](https://img.shields.io/badge/Pipeline-Ativa%20Diariamente-brightgreen?style=for-the-badge)](https://github.com/Dom1ng0s/Gado-Scraper/actions)

> Pipeline de dados que coleta automaticamente as cotações de **boi gordo** e **novilha** todos os dias — sem servidores, sem custos, sem intervenção manual. O próprio GitHub vira a infraestrutura.

</div>

---

## 💡 A Ideia por Trás do Projeto

Pecuaristas tomam decisões de compra e venda baseadas nas cotações do dia. O problema: essas informações estão espalhadas em sites de difícil automação e não existem APIs públicas confiáveis para o setor.

O Gado-Scraper resolve isso com uma abordagem elegante e de custo zero:

- **GitHub Actions** age como um cron job na nuvem, rodando os scrapers todo dia
- **O próprio repositório** funciona como banco de dados histórico — cada commit é um snapshot do preço naquele dia
- **Sem infraestrutura própria** — sem servidor, sem banco de dados, sem custos de cloud

---

## ⚙️ Como a Pipeline Funciona

```
┌─────────────────────────────────────────────────────┐
│              GitHub Actions (todo dia)               │
│                                                      │
│  1. Checkout do repositório                          │
│  2. pip install -r requirements.txt                  │
│  3. python scraper_boi.py     ──► cotacoes_boi_hoje.json     │
│  4. python scraper_novilha.py ──► cotacoes_novilha_hoje.json │
│  5. git commit + git push (atualiza o repositório)   │
└─────────────────────────────────────────────────────┘
```

O arquivo `.github/workflows/` contém o workflow agendado com **cron expression**, que dispara automaticamente em horário de mercado.

---

## 📊 Formato dos Dados Coletados

Os scrapers exportam os dados em JSON estruturado, prontos para consumo por qualquer sistema:

**`cotacoes_boi_hoje.json`**
```json
[
  {
    "data": "2026-02-24",
    "categoria": "Boi Gordo",
    "preco_arroba": "R$ 320,50",
    "regiao": "São Paulo",
    "fonte": "..."
  }
]
```

**`cotacoes_novilha_hoje.json`**
```json
[
  {
    "data": "2026-02-24",
    "categoria": "Novilha",
    "preco_arroba": "R$ 290,00",
    "regiao": "Mato Grosso",
    "fonte": "..."
  }
]
```

> 💾 **O histórico de preços está preservado no git log** — cada commit diário é um ponto de dado para análise de séries temporais.

---

## 🛠️ Stack Tecnológica

| Responsabilidade | Tecnologia |
|---|---|
| **Linguagem** | Python 3.10+ |
| **Scraping** | Requests + BeautifulSoup4 |
| **Automação / CI** | GitHub Actions (Cron) |
| **Armazenamento** | JSON no próprio repositório |
| **Versionamento histórico** | Git (cada commit = snapshot diário) |

---

## 🗂️ Estrutura do Projeto

```
Gado-Scraper/
├── .github/
│   └── workflows/
│       └── daily_scrape.yml      # Cron job: roda todo dia automaticamente
├── scraper_boi.py                # Coleta cotações de boi gordo
├── scraper_novilha.py            # Coleta cotações de novilha
├── cotacoes_boi_hoje.json        # Dados mais recentes (atualizado pela pipeline)
├── cotacoes_novilha_hoje.json    # Dados mais recentes (atualizado pela pipeline)
└── requirements.txt
```

---

## 🚀 Como Rodar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/Dom1ng0s/Gado-Scraper.git
cd Gado-Scraper

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute os scrapers manualmente
python scraper_boi.py
python scraper_novilha.py
```

Os arquivos JSON serão gerados/atualizados na raiz do projeto.

---

## 🔧 Como Fazer o Fork e Usar no Seu Repositório

A pipeline roda automaticamente em qualquer fork. Basta:

1. Fazer o fork do repositório
2. Ir em **Settings → Actions → General** e habilitar os workflows
3. O GitHub Actions vai rodar o scraper automaticamente todo dia

> Nenhuma configuração adicional necessária — sem variáveis de ambiente, sem tokens de API.

---

## 🗺️ Próximas Evoluções

- [ ] Notificação via Telegram quando o preço ultrapassar um threshold
- [ ] Dashboard com histórico de variações (Streamlit ou Grafana)
- [X] Integração direta com o [sistema_gado](https://github.com/Dom1ng0s/sistema_gado) para alimentar cotações em tempo real
- [ ] Exportação para CSV para análise em Excel/Pandas

---

## 👤 Autor

**Davi Domingos de Oliveira**
Estudante de Ciência da Computação — UFAL | Backend Developer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/davidomingosdeoliveira/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/Dom1ng0s)
[![Email](https://img.shields.io/badge/Email-D14836?style=flat&logo=gmail&logoColor=white)](mailto:odomingosdavi@gmail.com)
