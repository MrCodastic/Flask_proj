from flask import Blueprint, request, jsonify, render_template
from app.services.fraud_engine import fraud_service

api_bp = Blueprint('api', __name__)

# --- 1. THE EXISTING API (For Computers/CURL) ---
@api_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        result = fraud_service.predict(
            amount=data.get('amount'),
            ip_risk=data.get('ip_risk'),
            time=data.get('time')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- 2. THE NEW DASHBOARD (For Humans/Browser) ---
@api_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    result = None
    
    if request.method == 'POST':
        # NOTE: We use request.form (NOT json) because it's an HTML form
        # We convert strings to float because HTML sends everything as text
        try:
            amount = float(request.form['amount'])
            ip_risk = float(request.form['ip_risk'])
            time = float(request.form['time'])
            
            # REUSE THE SAME ENGINE!
            result = fraud_service.predict(amount, ip_risk, time)
            
        except ValueError:
            result = {"error": "Invalid input numbers"}

    # Render the HTML template and pass the result (if any)
    return render_template('fraud_dashboard.html', result=result)