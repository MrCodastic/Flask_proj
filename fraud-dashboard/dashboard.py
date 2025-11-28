import streamlit as st
import joblib
import numpy as np
import os

# --- 1. SETUP & MODEL LOADING ---
st.set_page_config(page_title="Fraud Hunter", page_icon="🕵️")

@st.cache_resource
def load_model():
    # Streamlit needs caching, or it reloads the model on every click!
    if os.path.exists('model.pkl'):
        return joblib.load('model.pkl')
    else:
        return None

model = load_model()

# --- 2. THE UI (FRONTEND) ---
st.title("🕵️ Fraud Detection Dashboard")
st.markdown("Use the sliders to simulate a transaction.")

col1, col2 = st.columns(2)
with col1:
    amount = st.number_input("Transaction Amount ($)", min_value=0, max_value=10000, value=500)
    time = st.slider("Time of Day (24h)", 0, 24, 12)

with col2:
    ip_risk = st.slider("IP Risk Score (0=Safe, 1=Risky)", 0.0, 1.0, 0.1)

# --- 3. THE LOGIC (BACKEND) ---
# In Flask, this was in 'services/fraud_engine.py'. Here, it is mixed in.
if st.button("Analyze Transaction"):
    if model:
        features = np.array([[amount, ip_risk, time]])
        prob = model.predict_proba(features)[0][1]
        
        st.divider()
        st.subheader("Analysis Result")
        
        # Visualizing the Output
        st.metric(label="Fraud Probability", value=f"{prob:.2%}")
        
        if prob > 0.7:
            st.error("🚨 BLOCKED: High Risk Transaction Detected")
            st.json({
                "status": "BLOCKED",
                "reason": "Risk Score > 0.7",
                "risk_score": prob
            })
        else:
            st.success("✅ APPROVED: Transaction looks safe")
            st.balloons()
    else:
        st.error("Model not found! Run make_model.py first.")

# --- 4. DEBUGGING INFO ---
with st.expander("See Raw Inputs"):
    st.write(f"Inputs: Amount={amount}, IP={ip_risk}, Time={time}")
