from flask import Flask, request
import requests
import math

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

    # Entrada: média entre close e último high/low
    entry = (close + (high if direction == "UP" else low)) / 2

    # SL: penúltimo swing high/low — simplificado como high/low (poderias integrar com histórico)
    stop_loss = low if direction == "UP" else high

    # Diferença entre entrada e SL
    risk_per_unit = abs(entry - stop_loss)

    if risk_per_unit == 0:
        return None

    # Cálculo do tamanho da posição
    size = RISK_USD / risk_per_unit
    size = math.floor(size * 1000) / 1000  # arredondar

    # TP: RR de 1.25:1
    take_profit = entry + (risk_per_unit * RR) if direction == "UP" else entry - (risk_per_unit * RR)

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
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    trade = calcular_trade(data)

    if trade:
        mensagem = (
            f"*SINAL ONDUSDT 📈*\n"
            f"Direção: *{trade['direction']}*\n"
            f"Entrada: `{trade['entry']}`\n"
            f"SL: `{trade['stop_loss']}`\n"
            f"TP: `{trade['take_profit']}`\n"
            f"Tamanho: `{trade['size']}` unidades\n"
            f"Risco: ${RISK_USD}"
        )
        enviar_telegram(mensagem)

    return "OK", 200
