import joblib
import numpy as np
import os

class FraudEngine:
    def __init__(self):
        # Robust path finding for the model
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, '../models/artifacts/model.pkl')
        
        try:
            self.model = joblib.load(model_path)
            print("✅ Model loaded successfully from", model_path)
        except FileNotFoundError:
            print(f"❌ ERROR: Model not found at {model_path}. Run training script first!")
            self.model = None

    def predict(self, amount, ip_risk, time):
        if not self.model:
            return {"error": "Model not loaded"}
            
        features = np.array([[amount, ip_risk, time]])
        prob = self.model.predict_proba(features)[0][1]
        is_fraud = prob > 0.7
        
        return {
            "fraud_probability": round(float(prob), 4),
            "is_blocked": bool(is_fraud),
            "risk_level": "CRITICAL" if is_fraud else "NORMAL"
        }

# Singleton instance
fraud_service = FraudEngine()
