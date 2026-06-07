"""
Como adicionar os secrets no GitHub Actions:
  1. Acesse github.com/<seu-usuario>/Gado-Scraper/settings/secrets/actions
  2. Clique em "New repository secret"
  3. Adicione TELEGRAM_TOKEN  → token do bot (ex: 123456:ABC-DEF...)
  4. Adicione TELEGRAM_CHAT_ID → ID do chat/canal que receberá os alertas
     (use @userinfobot no Telegram para descobrir seu chat_id)

Os secrets ficam disponíveis no workflow via ${{ secrets.NOME_DO_SECRET }}
e chegam ao Python como variáveis de ambiente (env:).
"""

import os
import sys

import requests

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_alert(mensagem: str) -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print(
            "[notificador] TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos — alerta ignorado.",
            file=sys.stderr,
        )
        return

    try:
        resp = requests.post(
            _API_URL.format(token=token),
            json={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"},
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[notificador] Alerta enviado ao Telegram.")
    except Exception as e:
        # Falha no notificador nunca deve derrubar o processo principal
        print(f"[notificador] Falha ao enviar alerta: {e}", file=sys.stderr)


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Alerta sem mensagem definida."
    send_alert(msg)
