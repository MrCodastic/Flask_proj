import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIGURATION ---
st.set_page_config(page_title="Human Behavior Twin: Anakin Skywalker", layout="wide")

st.title("🧠 Human Behavior Twin: The Fall of Anakin Skywalker")
st.markdown("""
This model simulates the internal emotional state of a character using **Russell's Circumplex Model**.
We feed external "Life Events" into the twin, and its internal math determines its current **Valence** (Mood) and **Arousal** (Energy).
""")

# --- THE TIMELINE DATA (The Input Stream) ---
# V = Valence impact (-1 to +1), A = Arousal impact (-1 to +1)
timeline = [
    {"step": 1, "event": "Baseline state (Slave on Tatooine)", "v_impact": 0.0, "a_impact": 0.0},
    {"step": 2, "event": "Discovery by Qui-Gon & Podrace Win", "v_impact": 0.6, "a_impact": 0.4},
    {"step": 3, "event": "Separated from Mother (Leaving home)", "v_impact": -0.4, "a_impact": 0.3},
    {"step": 4, "event": "Rejected by Jedi Council initially", "v_impact": -0.3, "a_impact": 0.2},
    {"step": 5, "event": "Qui-Gon dies (Loss of father figure)", "v_impact": -0.6, "a_impact": 0.1},
    {"step": 6, "event": "Time Jump: Teenager, powerful but arrogant", "v_impact": 0.2, "a_impact": 0.1},
    {"step": 7, "event": "Nightmares of Mother dying", "v_impact": -0.5, "a_impact": 0.6},
    {"step": 8, "event": "Mother dies in his arms on Tatooine", "v_impact": -1.0, "a_impact": 0.8},
    {"step": 9, "event": "Slaughters the Tusken Raiders", "v_impact": -0.2, "a_impact": 0.9},
    {"step": 10, "event": "Secret marriage to Padme", "v_impact": 0.7, "a_impact": -0.3},
    {"step": 11, "event": "Clone Wars begin (General Skywalker)", "v_impact": 0.1, "a_impact": 0.5},
    {"step": 12, "event": "Visions of Padme dying in childbirth", "v_impact": -0.6, "a_impact": 0.7},
    {"step": 13, "event": "Denied rank of Master by Council", "v_impact": -0.4, "a_impact": 0.8},
    {"step": 14, "event": "Palpatine reveals he is Sith Lord", "v_impact": -0.3, "a_impact": 0.9},
    {"step": 15, "event": "Betrays Mace Windu to save Palpatine", "v_impact": -0.8, "a_impact": 1.0},
    {"step": 16, "event": "Order 66 / March on Jedi Temple", "v_impact": -0.9, "a_impact": 0.6},
    {"step": 17, "event": "Chokes Padme on Mustafar", "v_impact": -1.0, "a_impact": 1.0},
    {"step": 18, "event": "Defeated by Obi-Wan, burns alive", "v_impact": -1.0, "a_impact": -0.5},
    {"step": 19, "event": "Reborn as Darth Vader suit", "v_impact": -0.9, "a_impact": -0.8},
]

# --- THE TWIN MODEL (The Logic) ---
class EmotionalTwin:
    def __init__(self):
        # Initial State: Slightly negative valence (slave), low arousal (calm)
        self.valence = -0.1
        self.arousal = -0.2
        self.history_v = [self.valence]
        self.history_a = [self.arousal]
        # Emotional Inertia: How much previous state lingers (0 to 1)
        # A high number means it takes a lot to change their mood.
        self.inertia = 0.75 

    def process_event(self, v_impact, a_impact):
        # The Core Twin Formula:
        # New State = (Old State * Inertia) + (New Event Impact * (1-Inertia))
        
        # Calculate new RAW state based on impact
        new_v_raw = self.valence + v_impact
        new_a_raw = self.arousal + a_impact

        # Apply Inertia (Weighted average of old state and new impact)
        self.valence = (self.valence * self.inertia) + (new_v_raw * (1 - self.inertia))
        self.arousal = (self.arousal * self.inertia) + (new_a_raw * (1 - self.inertia))

        # Clamp values between -1.0 and 1.0 boundary
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(-1.0, min(1.0, self.arousal))
        
        self.history_v.append(self.valence)
        self.history_a.append(self.arousal)

# Initialize Session State
if 'twin' not in st.session_state:
    st.session_state['twin'] = EmotionalTwin()
if 'step_index' not in st.session_state:
    st.session_state['step_index'] = 0

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Controls")
current_step_idx = st.session_state['step_index']

# Get current event data
if current_step_idx < len(timeline):
    current_event_data = timeline[current_step_idx]
    st.sidebar.subheader(f"Step {current_event_data['step']}: Current Event")
    st.sidebar.info(f"**{current_event_data['event']}**")
    
    st.sidebar.write(f"Valence Impact: {current_event_data['v_impact']}")
    st.sidebar.write(f"Arousal Impact: {current_event_data['a_impact']}")
    
    if st.sidebar.button("▶️ Process Event & Advance State"):
        # Process the event into the Twin
        st.session_state['twin'].process_event(
            current_event_data['v_impact'],
            current_event_data['a_impact']
        )
        # Advance step
        st.session_state['step_index'] += 1
        st.rerun()

else:
    st.sidebar.success("Simulation Complete. Anakin is now Vader.")
    if st.sidebar.button("🔄 Reset Simulation"):
        st.session_state['twin'] = EmotionalTwin()
        st.session_state['step_index'] = 0
        st.rerun()

# --- VISUALIZATION FUNCTION ---
def plot_circumplex(twin):
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # 1. Setup the quadrants background
    # Top Right (Happy/Excited) - Yellow/Orange tint
    ax.add_patch(patches.Rectangle((0, 0), 1, 1, color='#ffeb99', alpha=0.3))
    # Top Left (Angry/Fearful) - Red tint
    ax.add_patch(patches.Rectangle((-1, 0), 1, 1, color='#ff9999', alpha=0.3))
    # Bottom Left (Sad/Depressed) - Blue tint
    ax.add_patch(patches.Rectangle((-1, -1), 1, 1, color='#9999ff', alpha=0.3))
    # Bottom Right (Calm/Content) - Green tint
    ax.add_patch(patches.Rectangle((0, -1), 1, 1, color='#99ff99', alpha=0.3))

    # 2. Draw Axes
    ax.axhline(y=0, color='k', linewidth=1)
    ax.axvline(x=0, color='k', linewidth=1)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    
    # 3. Labels
    ax.text(1.15, 0, "Positive (Happy)", ha='left', va='center', fontweight='bold')
    ax.text(-1.15, 0, "Negative (Misery)", ha='right', va='center', fontweight='bold')
    ax.text(0, 1.15, "High Energy (Aroused)", ha='center', va='bottom', fontweight='bold')
    ax.text(0, -1.15, "Low Energy (Passive)", ha='center', va='top', fontweight='bold')
    
    # Quadrant Labels
    ax.text(0.5, 0.5, "EXCITED / JOY", ha='center', alpha=0.5)
    ax.text(-0.5, 0.5, "ANGRY / FEARFUL", ha='center', alpha=0.5)
    ax.text(-0.5, -0.5, "SAD / DEPRESSED", ha='center', alpha=0.5)
    ax.text(0.5, -0.5, "CALM / CONTENT", ha='center', alpha=0.5)

    # 4. Plot History Trajectory
    ax.plot(twin.history_v, twin.history_a, color='grey', linestyle='-', linewidth=1, marker='o', markersize=4, alpha=0.5)
    
    # 5. Plot Current State (Big Red Dot)
    ax.plot(twin.valence, twin.arousal, color='red', marker='o', markersize=15, markeredgecolor='black')
    
    # Title current state
    ax.set_title(f"Current State: V={twin.valence:.2f}, A={twin.arousal:.2f}")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    return fig

# --- MAIN LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Emotional State Map (Russell's Circumplex)")
    fig = plot_circumplex(st.session_state['twin'])
    st.pyplot(fig)

with col2:
    st.subheader("State Analysis")
    v = st.session_state['twin'].valence
    a = st.session_state['twin'].arousal
    
    # Determine qualitative state
    emotional_label = "Neutral"
    if v > 0.2 and a > 0.2: emotional_label = "Happy / Excited"
    elif v > 0.2 and a < -0.2: emotional_label = "Calm / Content"
    elif v < -0.2 and a > 0.2: emotional_label = "Stressed / Angry"
    elif v < -0.2 and a < -0.2: emotional_label = "Sad / Depressed"
    
    st.metric("Primary Emotion", emotional_label)
    
    st.progress((v + 1) / 2, text=f"Valence (Mood): {v:.2f}")
    st.progress((a + 1) / 2, text=f"Arousal (Energy): {a:.2f}")
    
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("The model uses `Inertia`. A single happy event won't instantly make a depressed person ecstatic. The current state is a weighted average of the past state and the new event's impact.")