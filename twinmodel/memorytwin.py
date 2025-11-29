import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Memory Agent Twin", layout="wide")

st.title("🧠 The Spaced Repetition Memory Agent")
st.markdown("""
This Digital Twin models **Human Memory Decay**.
* **Without Agent:** You learn once, and the memory fades to zero.
* **With Agent:** The Agent "pings" you exactly when you are about to forget, resetting the curve.
""")

# --- 1. CONFIGURATION ---
st.sidebar.header("Brain Parameters")
initial_stability = st.sidebar.slider("Initial Memory Stability (Days)", 0.5, 5.0, 1.0, help="How long the memory lasts after the FIRST exposure.")
learning_rate = st.sidebar.slider("IQ / Learning Efficiency", 1.1, 3.0, 2.0, help="How much stronger the memory gets after a review. (2.0 = Doubles stability)")

st.sidebar.header("Agent Strategy")
reminder_threshold = st.sidebar.slider("Remind me when Retention drops to:", 0.1, 0.95, 0.85)

# --- 2. THE MEMORY MODEL (The Twin) ---
def simulate_memory(days=60, with_agent=False):
    # State
    retention = 1.0  # Starts at 100%
    stability = initial_stability # How fast it decays (Higher = Slower decay)
    time_since_review = 0
    
    history = {'day': [], 'retention': [], 'event': []}
    
    for day in range(days):
        # Physics of Forgetting: R = e^(-t/S)
        retention = np.exp(-time_since_review / stability)
        
        event = "None"
        
        if with_agent:
            # AGENT LOGIC: If memory drops below threshold, Trigger Reminder
            if retention < reminder_threshold:
                # 1. Reset Retention to 100%
                retention = 1.0
                # 2. Reset Timer
                time_since_review = 0
                # 3. Increase Stability (The "Spaced Repetition" Magic)
                # The harder it was to remember, the more you learn. 
                stability = stability * learning_rate 
                event = "Reminder"
            else:
                time_since_review += 1
        else:
            time_since_review += 1
            
        history['day'].append(day)
        history['retention'].append(retention)
        history['event'].append(event)
        
    return pd.DataFrame(history)

# --- 3. RUN SIMULATION ---
col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🚀 Run Simulation"):
        df_natural = simulate_memory(with_agent=False)
        df_agent = simulate_memory(with_agent=True)
        
        # Count Reminders
        reminders = df_agent[df_agent['event'] == "Reminder"].shape[0]
        final_retention_nat = df_natural.iloc[-1]['retention']
        final_retention_agt = df_agent.iloc[-1]['retention']
        
        st.metric("Reminders Sent", reminders)
        st.metric("Retention (With Agent)", f"{final_retention_agt*100:.1f}%")
        st.metric("Retention (Natural)", f"{final_retention_nat*100:.1f}%", delta_color="inverse")

with col1:
    # Visualize
    df_natural = simulate_memory(with_agent=False)
    df_agent = simulate_memory(with_agent=True)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot Natural Decay (Red)
    ax.plot(df_natural['day'], df_natural['retention'], color='red', linestyle='--', alpha=0.5, label='Natural Forgetting')
    ax.fill_between(df_natural['day'], df_natural['retention'], color='red', alpha=0.1)
    
    # Plot Agent Intervention (Blue)
    ax.plot(df_agent['day'], df_agent['retention'], color='blue', linewidth=2, label='With Memory Agent')
    ax.fill_between(df_agent['day'], df_agent['retention'], color='blue', alpha=0.1)
    
    # Plot Threshold Line
    ax.axhline(y=reminder_threshold, color='green', linestyle=':', label='Reminder Threshold')
    
    # Mark Reminder Points
    reminders = df_agent[df_agent['event'] == "Reminder"]
    ax.scatter(reminders['day'], reminders['retention'], color='blue', s=50, zorder=5)
    
    ax.set_title("Memory Retention Over Time")
    ax.set_ylabel("Memory Strength (Retention %)")
    ax.set_xlabel("Days")
    ax.set_ylim(0, 1.1)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    
    st.info("""
    **Observe the Blue Line:** Notice how the gaps between the "spikes" (reminders) get wider and wider? 
    That is **Neuroplasticity**. The Agent knows that every time you review, 
    you can wait longer before the next review.
    """)