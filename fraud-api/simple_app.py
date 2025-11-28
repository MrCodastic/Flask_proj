from flask import Flask, request, jsonify

app = Flask(__name__)

# --- FIX 1: THE FRONT DOOR (GET Request) ---
# This lets you open the link in Chrome/Edge and see something.
@app.route('/', methods=['GET'])
def home():
    return """
    <h1>✅ Flask is Working!</h1>
    <p>The server is running.</p>
    <p>To use the API, send a POST request to: <code>/predict</code></p>
    """

# --- FIX 2: THE API (POST Request) ---
# This is the "Machine" part. Browsers cannot easily test this, use CURL.
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    # Simple logic to prove it works
    amount = data.get('amount', 0)
    if amount > 1000:
        return jsonify({"status": "BLOCKED", "reason": "High Amount"})
    else:
        return jsonify({"status": "APPROVED", "message": "Transaction Safe"})

if __name__ == '__main__':
    # This prints the available routes to the console on start
    print("\n--- AVAILABLE ROUTES ---")
    print("1. Homepage: http://127.0.0.1:5000/  (Open in Browser)")
    print("2. API:      http://127.0.0.1:5000/predict (Use CURL)")
    print("------------------------\n")
    app.run(debug=True, port=5000)