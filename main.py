from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Novo token e chat_id confirmados
TELEGRAM_TOKEN = "7991116114:AAHtm1UmUR5CuPMpOkfhhpOGHmSo_9JxWQk"
TELEGRAM_CHAT_ID = "727463744"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem
    }
    requests.post(url, data=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data.get("symbol")
    direction = data.get("direction")
    close = data.get("close")

    mensagem = f"🚨 SINAL DETETADO 🚨\n\nPar: {symbol}\nDireção: {direction}\nPreço de Fecho: {close}"
    enviar_telegram(mensagem)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
