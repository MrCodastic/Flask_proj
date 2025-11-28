import xgboost as xgb
import joblib
import numpy as np

# Create dummy data
X = np.array([
    [10.0, 0.1, 14], 
    [5000.0, 0.9, 3], 
    [20.0, 0.2, 12], 
    [1000.0, 0.8, 2], 
])
y = np.array([0, 1, 0, 1])

print("Training dummy XGBoost model...")
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X, y)
joblib.dump(model, 'model.pkl')
print("✅ Model saved as model.pkl")
