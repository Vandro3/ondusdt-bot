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

    symbol = data.get("symbol")
    direction = data.get("direction")  # "DOWN" ou "UP"
    candle_close = data.get("candle_close")
    last_opposite_close = data.get("last_opposite_close")
    prev_opposite_close = data.get("prev_opposite_close")

    if None in [symbol, direction, candle_close, last_opposite_close, prev_opposite_close]:
        return "Dados em falta", 400

    # SHORT
    if direction == "DOWN":
        if prev_opposite_close > last_opposite_close:
            entry_price = (candle_close + last_opposite_close) / 2
            sl_price = prev_opposite_close
            tp_price = entry_price - (sl_price - entry_price) * 1.25

            mensagem = (
                f"📉 NOVO SHORT - {symbol}\n"
                f"🔴 Direção: Baixa (EMA cruzamento para baixo)\n"
                f"📍 Fecho vela de cruzamento: {candle_close}\n"
                f"📘 Última vela verde (entrada): {last_opposite_close}\n"
                f"🎯 Entrada: {round(entry_price, 5)}\n"
                f"🛑 SL: {round(sl_price, 5)}\n"
                f"🎯 TP: {round(tp_price, 5)}"
            )
            enviar_telegram(mensagem)
            return "Short enviado", 200
        else:
            return "SL inválido para SHORT", 400

    # LONG
    elif direction == "UP":
        if prev_opposite_close < last_opposite_close:
            entry_price = (candle_close + last_opposite_close) / 2
            sl_price = prev_opposite_close
            tp_price = entry_price + (entry_price - sl_price) * 1.25

            mensagem = (
                f"📈 NOVO LONG - {symbol}\n"
                f"🟢 Direção: Alta (EMA cruzamento para cima)\n"
                f"📍 Fecho vela de cruzamento: {candle_close}\n"
                f"📕 Última vela vermelha (entrada): {last_opposite_close}\n"
                f"🎯 Entrada: {round(entry_price, 5)}\n"
                f"🛑 SL: {round(sl_price, 5)}\n"
                f"🎯 TP: {round(tp_price, 5)}"
            )
            enviar_telegram(mensagem)
            return "Long enviado", 200
        else:
            return "SL inválido para LONG", 400

    return "Direção não suportada", 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
