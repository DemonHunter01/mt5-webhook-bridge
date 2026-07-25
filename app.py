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
        if len(parts) >= 3:
            action = f"{parts[0]} {parts[1]}".lower()  # e.g., "buy stop"
            
            # Round the reference price to 2 decimal places
            ref_price = round(float(parts[2]), 2)     # e.g., 3440.313 becomes 3440.31
            
            signal_queue.append({"action": action, "ref_price": ref_price})
            print(f"Queued Signal: {action} @ {ref_price}")
            return jsonify({"status": "queued", "ref_price": ref_price}), 200
            
        return jsonify({"error": "Invalid format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# MT5 EA calls this endpoint to get orders
@app.route('/get-signal', methods=['GET'])
def get_signal():
    if signal_queue:
        return jsonify(signal_queue.pop(0)), 200
    return jsonify({"action": "none"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
