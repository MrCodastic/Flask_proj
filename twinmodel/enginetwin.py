import streamlit as st
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="Industrial Fan Digital Twin", layout="wide")

st.title("⚙️ Industrial Fan: Predictive Maintenance Twin")
st.markdown("""
**Scenario:** A cooling fan in a server farm.
* **Red Line (Real):** The actual vibration sensor data.
* **Green Line (Twin):** The physics model predicting what vibration *should* be.
* **The Gap:** If Red diverges from Green, we have a mechanical fault.
""")

# --- CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    st.info("Control Panel")
    start_btn = st.button("▶️ Start Monitoring")
    # A toggle to break the machine intentionally
    force_break = st.checkbox("🔨 Simulate Bearing Failure")

# --- TWIN LOGIC ---
class DigitalTwinSystem:
    def __init__(self):
        self.time_step = 0
    
    def get_data(self, is_broken):
        self.time_step += 0.1
        
        # 1. Simulate RPM (Sine wave pattern)
        rpm = 1000 + 200 * np.sin(self.time_step)
        
        # 2. Physics Model (The Twin's Prediction)
        # "Healthy vibration is proportional to RPM squared"
        expected_vibration = (rpm / 1000) ** 2
        
        # 3. Real World Data (With Noise + Potential Faults)
        noise = np.random.normal(0, 0.05)
        
        if is_broken:
            # If broken, vibration is 3x higher than physics predicts
            actual_vibration = (expected_vibration * 3.0) + noise
        else:
            # If healthy, it matches physics + noise
            actual_vibration = expected_vibration + noise
            
        return rpm, actual_vibration, expected_vibration

# --- VISUALIZATION LOOP ---
if start_btn:
    system = DigitalTwinSystem()
    
    # Placeholders for live updates
    metric_placeholder = st.empty()
    chart_placeholder = st.empty()
    alert_placeholder = st.empty()
    
    # Data buffer
    history = {'Time': [], 'Real Vibration': [], 'Expected (Twin)': []}
    
    for i in range(100): # Run for 100 frames
        # Get Data
        rpm, real_vib, expected_vib = system.get_data(is_broken=force_break)
        
        # Calculate Deviation (The "Residual")
        deviation = abs(real_vib - expected_vib)
        
        # Update Data History
        history['Time'].append(i)
        history['Real Vibration'].append(real_vib)
        history['Expected (Twin)'].append(expected_vib)
        
        # Convert to DataFrame for easy plotting
        df = pd.DataFrame(history)
        
        # 1. Update Metrics
        with metric_placeholder.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("Current RPM", f"{int(rpm)}")
            c2.metric("Vibration Sensor", f"{real_vib:.2f}")
            c3.metric("Twin Prediction", f"{expected_vib:.2f}")

        # 2. Check for Anomaly
        if deviation > 0.5:
             alert_placeholder.error(f"🚨 ANOMALY DETECTED! Deviation: {deviation:.2f}")
        else:
             alert_placeholder.success("✅ System Nominal")

        # 3. Update Chart
        # We use Streamlit's native line chart which handles live data better than matplotlib here
        chart_data = df.set_index('Time')[['Real Vibration', 'Expected (Twin)']]
        chart_placeholder.line_chart(chart_data, color=["#FF0000", "#00FF00"]) 
        # Note: Colors map alphabetically to columns usually, but this distinguishes the two lines.
        
        time.sleep(0.1)
        