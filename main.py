from flask import Flask, request
import requests
import math
import os

app = Flask(__name__)

# Telegram config
TELEGRAM_TOKEN = "7856624794:AAHA_0Tu01XokJtg4p4eoqeLh4Rp_NvY6ck"
TELEGRAM_CHAT_ID = "727463744"

# Risco fixo
RISK_USD = 5.0
RR = 1.25

def calcular_trade(data):
    direction = data["direction"]
    close = float(data["close"])
    high = float(data["high"])
    low = float(data["low"])
    symbol = data["symbol"]

    # Entrada: média entre close e high/low dependendo da direção
    entry = (close + (high if direction == "UP" else low)) / 2

    # SL: simplificado como high/low contrário à direção (podes melhorar depois com swing real)
    stop_loss = low if direction == "UP" else high

    risk_per_unit = abs(entry - stop_loss)
    if risk_per_unit == 0:
        return None

    size = RISK_USD / risk_per_unit
    size = math.floor(size * 1000) / 1000  # arredondar

    take_profit = entry + risk_per_unit * RR if direction == "UP" else entry - risk_per_unit * RR

    return {
        "symbol": symbol,
        "direction": direction,
        "entry": round(entry, 4),
        "stop_loss": round(stop_loss, 4),
        "take_profit": round(take_profit, 4),
        "size": round(size, 3)
    }

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    trade = calcular_trade(data)

    if trade:
        mensagem = (
            f"*SINAL {trade['symbol']}*\n"
            f"📊 Direção: *{trade['direction']}*\n"
            f"🎯 Entrada: `{trade['entry']}`\n"
            f"❌ SL: `{trade['stop_loss']}`\n"
            f"✅ TP: `{trade['take_profit']}`\n"
            f"💰 Tamanho: `{trade['size']}` unidades\n"
            f"⚠️ Risco: ${RISK_USD}"
        )
        enviar_telegram(mensagem)

    return "OK", 200

# Iniciar servidor com a PORT do Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
