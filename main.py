from flask import Flask, request
import requests
import os

app = Flask(__name__)

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
    candle_close = data.get("candle_close")
    aux_close = data.get("last_red_close") if direction == "UP" else data.get("last_green_close")

    if candle_close is None or aux_close is None:
        return "Missing data", 400

    # Cálculo da entrada
    entry_price = (candle_close + aux_close) / 2

    mensagem = (
        f"📈 NOVO SINAL - {symbol}\n"
        f"📊 Direção: {direction}\n"
        f"🟡 Fecho da vela: {candle_close}\n"
        f"🔵 Aux (última {'vermelha' if direction == 'UP' else 'verde'}): {aux_close}\n"
        f"🎯 Entrada calculada: {round(entry_price, 5)}"
    )

    enviar_telegram(mensagem)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
