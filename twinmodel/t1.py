import streamlit as st
import numpy as np
import time
import random
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Workplace Digital Twin", layout="wide")

st.title("🏢 Social Digital Twin: Workplace Rumor Simulation")
st.markdown("""
This Digital Twin simulates how information (or a virus) spreads through an office.
Adjust the parameters on the left and click **Start Simulation**.
""")

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.header("Twin Parameters")

grid_size = st.sidebar.slider("Office Size", 10, 100, 50)
virality = st.sidebar.slider("Virality (Spread Chance)", 0.0, 1.0, 0.3)
recovery = st.sidebar.slider("Boredom (Stop Chance)", 0.0, 1.0, 0.05)
speed = st.sidebar.slider("Simulation Speed (sec)", 0.01, 1.0, 0.1)

start_btn = st.sidebar.button("▶️ Start Simulation")

# --- 3. THE DIGITAL TWIN LOGIC (Backend) ---
class OfficeTwin:
    def __init__(self, size, spread_chance, recovery_chance):
        self.size = size
        self.spread_chance = spread_chance
        self.recovery_chance = recovery_chance
        # 0=Safe, 1=Infected/Rumor, 2=Recovered/Bored
        self.grid = np.zeros((size, size), dtype=int)
        # Patient Zero in the middle
        self.grid[size//2, size//2] = 1

    def update(self):
        new_grid = self.grid.copy()
        # Find all currently spreading agents
        rows, cols = np.where(self.grid == 1)
        
        for r, c in zip(rows, cols):
            # Infect Neighbors
            neighbors = [
                (r-1, c), (r+1, c), (r, c-1), (r, c+1)
            ]
            for nr, nc in neighbors:
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if self.grid[nr, nc] == 0:
                        if random.random() < self.spread_chance:
                            new_grid[nr, nc] = 1
            
            # Recovery/Boredom
            if random.random() < self.recovery_chance:
                new_grid[r, c] = 2
                
        self.grid = new_grid
        return self.grid

# --- 4. THE DASHBOARD (Frontend) ---

# Create placeholders for the live chart
col1, col2 = st.columns([3, 1])

with col1:
    chart_placeholder = st.empty()

with col2:
    stats_placeholder = st.empty()

if start_btn:
    # Initialize the Twin
    model = OfficeTwin(grid_size, virality, recovery)
    
    # Run for 100 steps
    for i in range(100):
        # Update Logic
        data = model.update()
        
        # Calculate Stats
        total_people = grid_size * grid_size
        infected = np.sum(data == 1)
        recovered = np.sum(data == 2)
        safe = total_people - infected - recovered
        
        # Update Stats Panel
        stats_placeholder.markdown(f"""
        ### Live Stats (Step {i})
        - 🟦 **Unaware:** {safe}
        - 🟥 **Spreading:** {infected}
        - ⬛ **Bored:** {recovered}
        """)

        # Update Visuals
        fig, ax = plt.subplots(figsize=(5, 5))
        # Custom Colors: Blue, Red, Grey
        cmap = plt.cm.colors.ListedColormap(['#e6f2ff', '#ff4b4b', '#4a4a4a'])
        ax.imshow(data, cmap=cmap, vmin=0, vmax=2)
        ax.set_axis_off()
        ax.set_title(f"Simulation Step: {i}")
        
        # Render in Streamlit
        chart_placeholder.pyplot(fig)
        
        # Close plot to save memory
        plt.close(fig)
        
        # Wait
        time.sleep(speed)