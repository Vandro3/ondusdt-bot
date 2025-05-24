from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Telegram configs
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

    # Dados recebidos
    symbol = data.get("symbol")
    direction = data.get("direction")
    candle_close = data.get("candle_close")  # vela de cruzamento
    last_green_close = data.get("last_green_close")
    prev_green_close = data.get("prev_green_close")  # possível SL

    if None in [symbol, direction, candle_close, last_green_close, prev_green_close]:
        return "Dados em falta", 400

    if direction == "DOWN":
        if prev_green_close > last_green_close:
            entry_price = (candle_close + last_green_close) / 2
            sl_price = prev_green_close

            mensagem = (
                f"📉 NOVO SHORT - {symbol}\n"
                f"🔴 Direção: {direction}\n"
                f"📍 Fecho vela de cruzamento: {candle_close}\n"
                f"📘 Última vela verde antes do cruzamento: {last_green_close}\n"
                f"🛑 SL (vela anterior com fecho maior): {sl_price}\n"
                f"🎯 Entrada: {round(entry_price, 5)}"
            )

            enviar_telegram(mensagem)
            return "OK", 200
        else:
            return "SL inválido: fecho anterior não é maior", 400

    return "Direção não suportada", 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
