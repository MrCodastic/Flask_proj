import xgboost as xgb
import joblib
import numpy as np
import os

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

# Save to the artifacts folder
save_path = 'app/models/artifacts/model.pkl'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
joblib.dump(model, save_path)
print(f"✅ Model saved to {save_path}")
