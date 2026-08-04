# Plano — Opção 1: múltiplas janelas de coleta por dia

Status: **proposto**, não implementado.
Data: 2026-07-28

---

## 1. Diagnóstico (o que motivou isto)

O workflow falha ~10% dos dias. A causa **não** é falta de cotação no fim de semana.
Todas as falhas têm a mesma assinatura:

```
ConnectTimeoutError: Connection to www.scotconsultoria.com.br timed out (connect timeout=15)
```

Evidências:

| Data | Dia | Resultado |
|---|---|---|
| 27/06 00:30 UTC | sáb | falha |
| 27/06 11:01 UTC | sáb | falha |
| 11/07 | sáb | falha |
| 13/07 | seg | falha |
| 23/07 | qui | falha |
| 25/07 | **sáb** | **sucesso** |
| 26/07 | dom | falha |
| 27/07 | seg | falha |

6 falhas em 57 execuções (~10,5%). Sábado passa, quinta falha — não é padrão de fim de semana.

Se fosse ausência de cotação, o sintoma seria outro: `RuntimeError("Tabela com 'Funrural'
não encontrada")` vindo do `_parse_table`, ou um JSON com 0 linhas salvo **sem erro** (o
`dropna` esvaziaria o DataFrame). Nunca `connect timeout`.

Hipótese principal: bloqueio geográfico/WAF do lado da Scot contra faixas de IP de
datacenter (runner do GitHub = Azure/EUA). O mesmo host responde em 0,43 s / HTTP 200 a
partir de IP brasileiro.

**Não confirmado.** Queda momentânea do site produziria timeout idêntico. O que aponta pra
bloqueio: é sempre `connect timeout`, nunca 5xx nem reset — a conexão TCP nem se
estabelece. Ver Fase 0.

---

## 2. Teto conhecido desta opção

Em 27/06 houve duas execuções separadas por **10h30** (00:30 e 11:01 UTC). As duas deram
timeout. Ou seja: pelo menos uma vez o bloqueio durou mais de meio dia, e espalhar as
tentativas ao longo do dia **não** teria salvado aquela data.

Isto reduz falhas, não elimina. Não há como estimar quanto sem medir a duração real dos
bloqueios (Fase 0 dá esse dado).

Solução com eficácia real, se um dia valer o custo: trocar o IP de saída — self-hosted
runner em máquina/VPS brasileira, ou proxy BR no `requests`. Fora do escopo deste plano.

---

## 3. Escopo

Arquivos tocados:

- `.github/workflows/atualizacao_diaria.yml`
- `scraper/base.py`

Sem dependências novas. Sem arquivos novos (fora este).

---

## Fase 0 — Confirmar a causa (opcional, 3 linhas)

Antes de tudo, vale saber se é bloqueio ao host ou rede do runner em geral. Step novo,
logo após instalar as libs:

```yaml
      - name: 3.5. Diagnóstico de rede
        continue-on-error: true
        run: |
          curl -sS -o /dev/null -w "scot: %{http_code} em %{time_total}s\n" --max-time 20 https://www.scotconsultoria.com.br/cotacoes/boi-gordo/ || echo "scot: FALHOU"
          curl -sS -o /dev/null -w "controle(gov.br): %{http_code} em %{time_total}s\n" --max-time 20 https://www.gov.br/ || echo "controle: FALHOU"
```

`continue-on-error` para o diagnóstico nunca derrubar o job.

Leitura no próximo dia ruim:

- scot falha **e** controle passa → bloqueio específico ao host. Confirma a hipótese.
- os dois falham → problema de rede/saída do runner, outro tratamento.
- scot passa mas o Python falha → não é rede, é o `requests`/headers/TLS.

Pode ficar permanente, custa ~2s por run.

---

## Fase 1 — Três janelas de coleta

```yaml
on:
  schedule:
    - cron: '0 8 * * *'
    - cron: '0 13 * * *'
    - cron: '0 18 * * *'
  workflow_dispatch:
```

Por que 8/13/18 UTC:

- O GitHub atrasa jobs agendados de 1h a 3h (histórico observado: cron `0 9` disparando
  entre 10:00 e 15:26 UTC). Na prática caem em ~09-11, ~14-16, ~19-21 UTC.
- Tudo permanece **dentro do mesmo dia UTC**. Isso importa: ver a nota de fuso na Fase 2.
- Em BRT (UTC-3): ~06-08h, ~11-13h e ~16-18h. Cobre antes, durante e depois do horário
  comercial brasileiro.

Não colocar cron depois de ~20 UTC — com o atraso do GitHub a execução vira o dia UTC e a
checagem de "já coletei hoje" quebra.

---

## Fase 2 — Execuções seguintes viram "repescagem"

Sem isto, as três janelas raspam o site todo dia, geram commits redundantes e disparam
Telegram três vezes. Com isto, a 2ª e a 3ª só fazem trabalho se a 1ª falhou.

Em `scraper/base.py`:

```python
def _ja_coletado_hoje(output_path: str) -> bool:
    """True se o JSON existente já tem a data de hoje."""
    try:
        with open(output_path, encoding="utf-8") as f:
            return json.load(f)[0]["data_coleta"] == datetime.now().strftime("%Y-%m-%d")
    except (OSError, ValueError, IndexError, KeyError):
        return False
```

E no topo de `capturar_cotacoes`, antes do `_fetch_with_retry`:

```python
    if _ja_coletado_hoje(output_path):
        print(f"'{output_path}' já tem dados de hoje — nada a fazer.")
        return
```

Detalhes que importam:

- O `except` largo é intencional: arquivo ausente, JSON corrompido, lista vazia ou schema
  mudado → trata como "não coletado" e raspa. Falha para o lado seguro.
- Checa só o primeiro registro. Todos são escritos no mesmo `_clean`, com a mesma data.
- **Fuso:** o runner roda em UTC, então `data_coleta` é a data UTC — tanto na escrita
  quanto na comparação. É autoconsistente, por isso funciona. Só não é a data do mercado
  brasileiro em execuções perto da meia-noite UTC. Comportamento já existente hoje; este
  plano não muda. Se um dia precisar da data BRT, muda nos dois lugares junto.
- O boi e a novilha têm arquivos separados, logo checagens independentes: se um passou e o
  outro não, a repescagem refaz só o que faltou.

Teste (`test_ja_coletado.py`, roda com `python test_ja_coletado.py`):

```python
import json, os, tempfile
from datetime import datetime
from scraper.base import _ja_coletado_hoje

hoje = datetime.now().strftime("%Y-%m-%d")
d = tempfile.mkdtemp()

def escreve(nome, conteudo):
    p = os.path.join(d, nome)
    with open(p, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return p

assert _ja_coletado_hoje(os.path.join(d, "nao_existe.json")) is False
assert _ja_coletado_hoje(escreve("vazio.json", "[]")) is False
assert _ja_coletado_hoje(escreve("lixo.json", "{{{")) is False
assert _ja_coletado_hoje(escreve("velho.json", json.dumps([{"data_coleta": "2020-01-01"}]))) is False
assert _ja_coletado_hoje(escreve("hoje.json", json.dumps([{"data_coleta": hoje}]))) is True
print("ok")
```

---

## Fase 3 — Calar o ruído no Telegram

Com três janelas por dia, o alerta de falha dispararia 3x num dia ruim e o de sucesso 3x
num dia bom. Duas correções.

### 3a. Sucesso só quando algo mudou de fato

Step 6 ganha um `id` e um output:

```yaml
      - name: 6. Salvar arquivos no GitHub
        id: commit
        run: |
          git config --global user.name 'Bot do Scraper'
          git config --global user.email 'actions@github.com'

          git add cotacoes_boi_hoje.json cotacoes_novilha_hoje.json

          if git diff --staged --quiet; then
            echo "mudou=false" >> "$GITHUB_OUTPUT"
          else
            git commit -m "Dados atualizados: $(date +'%Y-%m-%d')"
            git push
            echo "mudou=true" >> "$GITHUB_OUTPUT"
          fi
```

Step 7:

```yaml
      - name: 7. Notificar sucesso no Telegram
        if: success() && steps.commit.outputs.mudou == 'true'
```

Efeito: a repescagem que não fez nada fica silenciosa. Um Telegram de sucesso por dia.

### 3b. Falha só na última janela

```yaml
      - name: 8. Notificar falha no Telegram
        if: failure() && (github.event_name != 'schedule' || github.event.schedule == '0 18 * * *')
```

`github.event.schedule` traz a string do cron que disparou. A cláusula `event_name` mantém
o alerta funcionando em `workflow_dispatch` (onde esse campo vem vazio).

Efeito: falha nas janelas 1 e 2 fica só no log do Actions; o Telegram só toca quando o dia
acabou sem dado. Se mudar os horários da Fase 1, **atualizar esta string junto** — é o
acoplamento chato deste plano.

---

## Fase 4 — Ajustes de custo (opcional)

O `nick-fields/retry` hoje faz 3 tentativas com 300s de espera (~15 min por scraper), e
dentro dele o Python ainda tenta 3x com 5s. Com três janelas no dia, essa insistência vira
redundante e queima minutos de runner à toa.

Sugestão: `max_attempts: 2`, `retry_wait_seconds: 60`. As janelas do dia passam a ser o
mecanismo de retry principal; o retry interno cobre só soluço momentâneo.

Guarda contra corrida no `git push`, caso duas execuções se sobreponham:

```yaml
concurrency:
  group: raspagem
  cancel-in-progress: false
```

Improvável com janelas de 5h, mas é uma linha.

---

## 4. Ordem de implementação

1. Fase 2 + teste, sozinha. Merge. Nada muda no comportamento (só uma janela ainda).
2. Fase 3, sozinha. Merge.
3. Fase 1 por último — é ela que multiplica as execuções.
4. Fase 0 e 4 quando der.

Nesta ordem, se algo quebrar, quebra com uma execução por dia e não com três.

---

## 5. Verificação

Depois do merge da Fase 1, num dia bom:

- 1ª janela: log `Sucesso Total! N linhas salvas`, um commit, um Telegram de sucesso.
- 2ª e 3ª: log `já tem dados de hoje — nada a fazer`, sem commit, sem Telegram.

Num dia ruim, checar no `gh run list` que as três rodaram e que o Telegram de falha veio
uma vez só.

Comando útil pra acompanhar o efeito ao longo de um mês:

```bash
gh run list --limit 100 --json conclusion,createdAt,event \
  -q '.[] | "\(.createdAt[0:10]) \(.createdAt[11:16]) \(.event) \(.conclusion)"' | sort
```

Métrica: dias **sem nenhum dado coletado** (não runs falhos — agora um dia bom pode ter
uma janela falha e ainda assim terminar com dado). Base atual: 6 dias em 57.

---

## 6. Rollback

Reverter o commit. Nenhum estado externo é alterado — sem migração, sem schema, sem
secret novo. Voltar `on.schedule` a um único cron já neutraliza a mudança de
comportamento, mesmo com as Fases 2 e 3 no lugar.

---

## 7. Fora de escopo

- Trocar o IP de saída (self-hosted runner / proxy BR) — é o conserto de verdade, decisão
  separada.
- Fonte de dados alternativa como fallback.
- Histórico dos JSONs (hoje só o snapshot do dia é versionado).
