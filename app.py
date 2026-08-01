import os
from flask import Flask, request, jsonify

app = Flask(__name__)
signal_queue = []

@app.route('/', methods=['GET'])
def health_check():
    return "MT5 Webhook Bridge is live!", 200

# Receives alerts from TradingView
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        raw_data = request.get_data(as_text=True).strip()
        parts = raw_data.split()
        if not parts:
            return jsonify({"error": "Empty alert message"}), 400

        cmd = parts[0].lower()

        # 1. Cancel / Close Command (e.g. "cancel" or "close")
        if cmd in ["cancel", "close"]:
            signal = {"action": "cancel", "ref_price": 0.0}
            signal_queue.append(signal)
            print("[ACTION] Queued CANCEL/CLOSE ALL signal")
            return jsonify({"status": "queued", "action": "cancel"}), 200

        # 2. Order Command (e.g. "buy stop 3440.313")
        elif len(parts) >= 3:
            action = f"{parts[0]} {parts[1]}".lower()  # "buy stop" or "sell stop"
            ref_price = round(float(parts[2]), 2)     # Rounds to 2 decimal places
            
            signal = {"action": action, "ref_price": ref_price}
            signal_queue.append(signal)
            print(f"[ACTION] Queued Signal: {action} @ {ref_price}")
            return jsonify({"status": "queued", "signal": signal}), 200
            
        return jsonify({"error": "Invalid format"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# MT5 EA calls this endpoint to fetch orders
@app.route('/get-signal', methods=['GET'])
def get_signal():
    if signal_queue:
        return jsonify(signal_queue.pop(0)), 200
    return jsonify({"action": "none"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
