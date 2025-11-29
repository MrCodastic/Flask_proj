import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Network Influence Twin", layout="wide")

st.title("🕸️ Social Network Twin: Rumor vs. Truth")
st.markdown("""
**Realism Upgrade:** This uses a **Scale-Free Network**. 
Notice how some nodes (Influencers) are huge and connected to everyone, while others are small.
**Goal:** Quash the Red Rumor by injecting the Green Truth.
""")

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("Network Settings")
n_nodes = st.sidebar.slider("Population Size", 20, 100, 50)
rumor_virality = st.sidebar.slider("Rumor Strength", 0.1, 1.0, 0.6)
truth_potency = st.sidebar.slider("Truth/Correction Strength", 0.1, 1.0, 0.6)

st.sidebar.header("Counter-Strategy")
strategy = st.sidebar.radio(
    "Where to inject the Truth?",
    ("Random People (Inefficient)", "Top Influencers (Smart)")
)
injection_count = st.sidebar.slider("How many Truth Agents?", 1, 10, 3)

start_btn = st.sidebar.button("⚔️ Start Information War")

# --- SIMULATION LOGIC ---
def init_network(n):
    # Create a Barabasi-Albert graph (Real-world social network topology)
    # Each new node attaches to 2 existing nodes
    G = nx.barabasi_albert_graph(n, 2)
    
    # Calculate positions ONCE so the graph doesn't jump around
    pos = nx.spring_layout(G, seed=42)
    
    # Initialize States: 'neutral', 'rumor', 'truth'
    nx.set_node_attributes(G, 'neutral', 'state')
    
    # Identify Influencers (Nodes with most connections)
    degrees = dict(G.degree())
    top_influencers = sorted(degrees, key=degrees.get, reverse=True)[:5]
    
    return G, pos, top_influencers

def update_network(G, spread_prob, recover_prob):
    # We need a snapshot of current states to avoid cascading updates in one step
    current_states = nx.get_node_attributes(G, 'state')
    new_states = current_states.copy()
    
    nodes = list(G.nodes())
    random.shuffle(nodes) # Randomize order
    
    for node in nodes:
        my_state = current_states[node]
        neighbors = list(G.neighbors(node))
        
        # LOGIC: If I am INFECTED (Rumor), I try to spread it
        if my_state == 'rumor':
            for neighbor in neighbors:
                if current_states[neighbor] == 'neutral':
                    if random.random() < spread_prob:
                        new_states[neighbor] = 'rumor'
        
        # LOGIC: If I hold the TRUTH, I try to cure Rumors or immunize Neutrals
        elif my_state == 'truth':
            for neighbor in neighbors:
                neighbor_state = current_states[neighbor]
                
                # Quashing a Rumor (Harder)
                if neighbor_state == 'rumor':
                    if random.random() < recover_prob:
                        new_states[neighbor] = 'truth'
                
                # Immunizing a Neutral (Easier)
                elif neighbor_state == 'neutral':
                    if random.random() < recover_prob:
                        new_states[neighbor] = 'truth'
                        
    # Apply updates
    for node, state in new_states.items():
        G.nodes[node]['state'] = state
        
    return G

# --- VISUALIZATION ---
def draw_network(G, pos, ax):
    ax.clear()
    
    # Get states
    states = nx.get_node_attributes(G, 'state')
    
    # distinct lists for drawing
    neutral = [n for n, s in states.items() if s == 'neutral']
    rumor = [n for n, s in states.items() if s == 'rumor']
    truth = [n for n, s in states.items() if s == 'truth']
    
    # Scale node size by influence (degree)
    degrees = dict(G.degree())
    sizes = [degrees[n] * 30 for n in G.nodes()]
    
    # Draw Neutral (Grey)
    nx.draw_networkx_nodes(G, pos, nodelist=neutral, node_color='#cccccc', 
                           node_size=[degrees[n]*30 for n in neutral], ax=ax, label="Neutral")
    
    # Draw Rumor (Red)
    nx.draw_networkx_nodes(G, pos, nodelist=rumor, node_color='#ff4b4b', 
                           node_size=[degrees[n]*30 for n in rumor], ax=ax, label="Rumor")
    
    # Draw Truth (Green)
    nx.draw_networkx_nodes(G, pos, nodelist=truth, node_color='#00cc66', 
                           node_size=[degrees[n]*30 for n in truth], ax=ax, label="Truth")
    
    # Draw Edges
    nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
    
    ax.set_axis_off()
    ax.legend()

# --- MAIN APP ---
col1, col2 = st.columns([3, 1])
placeholder = col1.empty()
metrics = col2.empty()

if start_btn:
    G, pos, influencers = init_network(n_nodes)
    
    # 1. Start the Rumor (Patient Zero is a random non-influencer usually)
    patient_zero = random.choice([n for n in G.nodes() if n not in influencers])
    G.nodes[patient_zero]['state'] = 'rumor'
    
    # 2. Inject the Truth (Based on User Strategy)
    potential_agents = [n for n in G.nodes() if n != patient_zero]
    
    if strategy == "Top Influencers (Smart)":
        # Pick from the top connected nodes
        agents = influencers[:injection_count]
    else:
        # Pick random people
        agents = random.sample(potential_agents, injection_count)
        
    for agent in agents:
        G.nodes[agent]['state'] = 'truth'

    # Run Simulation
    for step in range(50):
        # Update Logic
        G = update_network(G, rumor_virality, truth_potency)
        
        # Count Stats
        states = list(nx.get_node_attributes(G, 'state').values())
        n_rumor = states.count('rumor')
        n_truth = states.count('truth')
        n_neutral = states.count('neutral')
        
        # Update Metrics
        metrics.markdown(f"""
        ### Step {step}
        - 🔴 **Rumor:** {n_rumor}
        - 🟢 **Truth:** {n_truth}
        - ⚪ **Neutral:** {n_neutral}
        
        **Strategy:** {strategy}
        """)
        
        # Draw
        fig, ax = plt.subplots(figsize=(8, 6))
        draw_network(G, pos, ax)
        placeholder.pyplot(fig)
        plt.close(fig)
        
        # Stop if one side wins completely
        if n_rumor == 0 or n_truth == 0:
            break
            
        time.sleep(0.1)