### 🚜 Gado-Scraper

**Pipeline automatizada para monitoramento diário de cotações pecuárias**

Pipeline de dados que coleta e agrega automaticamente as cotações de boi gordo e novilha de **33 praças pecuárias do Brasil** todos os dias. O sistema roda 100% na nuvem via GitHub Actions — sem servidores, sem custos de infraestrutura e sem intervenção manual.

---

#### 💡 O Problema que Este Projeto Resolve

Pecuaristas tomam decisões de compra e venda baseadas nas cotações do dia, mas essas informações estão espalhadas em dezenas de sites de difícil acesso e não existem APIs públicas confiáveis para o setor agropecuário.

O Gado-Scraper resolve isso com uma arquitetura de custo zero:
*   **GitHub Actions como Cron Job:** Um workflow automatizado dispara o scraper todos os dias no horário de fechamento do mercado.
*   **Git como Banco de Dados Histórico:** O próprio repositório funciona como armazenamento — cada commit diário é um snapshot de dados pronto para análise de séries temporais.
*   **Histórico em CSV:** Além dos commits, os dados acumulados ficam acessíveis diretamente em `data/` sem precisar parsear o git.
*   **Integração Direta:** Os dados gerados alimentam em tempo real o ERP (Sistema de Gestão de Gado).

---

#### 🏗️ Arquitetura do Pipeline (ETL)

![Arquitetura do Gado-Scraper](Gado-Scraper-Arch.png)

---

#### 📊 Formato dos Dados Coletados

Os scrapers exportam os dados em dois formatos:

**JSON do dia** (raiz do repositório):
*   `cotacoes_boi_hoje.json`
*   `cotacoes_novilha_hoje.json`

**Histórico acumulativo em CSV** (atualizado a cada execução):
*   `data/historico_boi.csv`
*   `data/historico_novilha.csv`

---

#### ⚙ Como a Pipeline Funciona

O workflow em `.github/workflows/atualizacao_diaria.yml` executa diariamente os seguintes passos:

1. `scraper_boi.py` e `scraper_novilha.py` fazem scraping e geram os JSONs do dia
2. `append_historico.py` appenda os novos registros aos CSVs históricos (com guarda contra duplicatas)
3. O commit diário salva tanto os JSONs quanto os CSVs atualizados
4. Uma notificação Telegram confirma o sucesso — ou alerta em caso de falha

A lógica de scraping é compartilhada em `scraper/base.py`, incluindo retry automático (3 tentativas, backoff de 5s) e timeout de 15s por requisição.

Para reconstruir o histórico completo a partir dos commits (útil após um fork):

```bash
pip install -r requirements.txt
python build_dataset.py
```

---

#### 🛠 Stack Tecnológica

| Responsabilidade | Tecnologia |
| ------ | ------ |
| **Linguagem** | Python 3.9+ |
| **Scraping** | Requests + pandas (`read_html`) |
| **Automação / CI** | GitHub Actions (Cron) |
| **Armazenamento** | JSON + CSV persistidos no repositório |
| **Alertas** | Telegram Bot API |
| **Versionamento histórico** | Git (commits diários automáticos) |

---

#### 🔧 Como Fazer o Fork e Usar na Sua Conta

A pipeline é 100% autossuficiente e roda automaticamente em qualquer *fork*.

1. Faça o fork deste repositório.
2. Vá em **Settings → Actions → General** e habilite `Read and write permissions`.
3. *(Opcional)* Para receber alertas no Telegram, adicione dois secrets em **Settings → Secrets and variables → Actions**:
   - `TELEGRAM_TOKEN` — token do seu bot
   - `TELEGRAM_CHAT_ID` — ID do chat que receberá as mensagens (use `@userinfobot` para descobrir o seu)
4. O GitHub Actions passará a rodar o scraper automaticamente na sua conta todos os dias.

Para rodar localmente:

```bash
pip install -r requirements.txt
python scraper_boi.py
python scraper_novilha.py
python append_historico.py
```

---

#### 🗺 Roadmap (Próximas Evoluções)

- [x] Integração direta com o `sistema_gado` para alimentar cotações em tempo real
- [x] Exportação automatizada para CSV (`data/historico_boi.csv`, `data/historico_novilha.csv`)
- [x] Notificações via Telegram (sucesso diário e alertas de falha)
- [ ] Dashboard com histórico de variações de preço (Streamlit ou Grafana)
- [ ] Alerta quando o preço em uma praça-chave ultrapassar um threshold configurável

---

#### 👤 Autor
**Davi Domingos de Oliveira**  
Estudante de Ciência da Computação — UFAL | Backend Developer
