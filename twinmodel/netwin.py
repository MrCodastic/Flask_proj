import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Multi-Network Twin", layout="wide")

st.title("🌐 Multi-Topology Digital Twin")
st.markdown("""
Test how rumors spread (and die) in different types of societies.
Select a **Network Topology** on the left to change the structure of connections.
""")

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("1. Choose Your Battlefield")
network_type = st.sidebar.selectbox(
    "Network Topology",
    ("Social Media (Scale-Free)", "The Village (Small World)", "Random Encounters (Erdos-Renyi)")
)

st.sidebar.header("2. Population Settings")
n_nodes = st.sidebar.slider("Population Size", 20, 100, 60)
rumor_virality = st.sidebar.slider("Rumor Strength (Red)", 0.1, 1.0, 0.5)
truth_potency = st.sidebar.slider("Truth Strength (Green)", 0.1, 1.0, 0.5)

st.sidebar.header("3. Counter-Strategy")
strategy = st.sidebar.radio(
    "Injection Strategy",
    ("Random People", "Highest Degree (Influencers)")
)
injection_count = st.sidebar.slider("Truth Agents", 1, 10, 3)

start_btn = st.sidebar.button("⚔️ Start Simulation")

# --- GRAPH GENERATION LOGIC ---
def get_network(n, type_name):
    if type_name == "Social Media (Scale-Free)":
        # Barabasi-Albert: New nodes prefer connecting to popular nodes
        G = nx.barabasi_albert_graph(n, 2)
        layout = nx.spring_layout(G, seed=42)
        desc = "Structure: A few massive 'Hubs' and many small nodes. (Like Twitter/X)"
        
    elif type_name == "The Village (Small World)":
        # Watts-Strogatz: High clustering (neighbors know neighbors)
        # k=4 (each node connects to 4 neighbors), p=0.1 (10% random rewiring)
        G = nx.watts_strogatz_graph(n, k=4, p=0.1)
        layout = nx.circular_layout(G) # Better for visualizing the 'ring' structure
        desc = "Structure: High clustering. Information travels effectively locally but slowly globally. (Like generic families/towns)"
        
    elif type_name == "Random Encounters (Erdos-Renyi)":
        # Random: Every node has probability p of connecting
        G = nx.erdos_renyi_graph(n, p=0.12)
        layout = nx.spring_layout(G, seed=42)
        desc = "Structure: Unstructured chaos. No clear hubs. (Like strangers at a conference)"
        
    return G, layout, desc

# --- UPDATE LOGIC ---
def update_network(G, spread_prob, recover_prob):
    current_states = nx.get_node_attributes(G, 'state')
    new_states = current_states.copy()
    nodes = list(G.nodes())
    random.shuffle(nodes)
    
    for node in nodes:
        my_state = current_states[node]
        neighbors = list(G.neighbors(node))
        
        if my_state == 'rumor':
            for neighbor in neighbors:
                if current_states[neighbor] == 'neutral':
                    if random.random() < spread_prob:
                        new_states[neighbor] = 'rumor'
        
        elif my_state == 'truth':
            for neighbor in neighbors:
                neighbor_state = current_states[neighbor]
                if neighbor_state == 'rumor':
                    if random.random() < recover_prob: # Cure
                        new_states[neighbor] = 'truth'
                elif neighbor_state == 'neutral':
                    if random.random() < recover_prob: # Immunize
                        new_states[neighbor] = 'truth'
    
    for node, state in new_states.items():
        G.nodes[node]['state'] = state
    return G

# --- VISUALIZATION ---
def draw_network(G, pos, ax):
    ax.clear()
    states = nx.get_node_attributes(G, 'state')
    
    neutral = [n for n, s in states.items() if s == 'neutral']
    rumor = [n for n, s in states.items() if s == 'rumor']
    truth = [n for n, s in states.items() if s == 'truth']
    
    # Calculate degree for sizing
    degrees = dict(G.degree())
    # Handle case where graph might be disconnected or empty
    if not degrees: return

    # Normalize sizes slightly
    sizes = [degrees[n] * 20 + 50 for n in G.nodes()]

    nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, nodelist=neutral, node_color='#dddddd', 
                           node_size=[degrees[n]*20+50 for n in neutral], ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=rumor, node_color='#ff4b4b', 
                           node_size=[degrees[n]*20+50 for n in rumor], ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=truth, node_color='#00cc66', 
                           node_size=[degrees[n]*20+50 for n in truth], ax=ax)
    
    ax.set_axis_off()

# --- MAIN APP ---
col1, col2 = st.columns([3, 1])
placeholder = col1.empty()
info_panel = col2.empty()

if start_btn:
    # 1. Setup
    G, pos, description = get_network(n_nodes, network_type)
    nx.set_node_attributes(G, 'neutral', 'state')
    
    # 2. Patient Zero (Rumor)
    # Pick a random node
    all_nodes = list(G.nodes())
    if all_nodes:
        patient_zero = random.choice(all_nodes)
        G.nodes[patient_zero]['state'] = 'rumor'
    
    # 3. Inject Truth Agents
    potential_agents = [n for n in all_nodes if n != patient_zero]
    
    if strategy == "Highest Degree (Influencers)":
        degrees = dict(G.degree())
        # Sort by degree high to low
        top_nodes = sorted(degrees, key=degrees.get, reverse=True)
        # Filter out patient zero
        top_nodes = [n for n in top_nodes if n != patient_zero]
        agents = top_nodes[:injection_count]
    else:
        agents = random.sample(potential_agents, min(len(potential_agents), injection_count))
        
    for agent in agents:
        G.nodes[agent]['state'] = 'truth'

    # 4. Loop
    for step in range(60):
        G = update_network(G, rumor_virality, truth_potency)
        
        states = list(nx.get_node_attributes(G, 'state').values())
        n_rumor = states.count('rumor')
        n_truth = states.count('truth')
        
        info_panel.info(description)
        info_panel.metric("Step", step)
        info_panel.markdown(f"""
        - 🔴 **Rumor:** {n_rumor}
        - 🟢 **Truth:** {n_truth}
        """)
        
        fig, ax = plt.subplots(figsize=(6, 6))
        draw_network(G, pos, ax)
        placeholder.pyplot(fig)
        plt.close(fig)
        
        if n_rumor == 0 or n_truth == 0:
            break
        time.sleep(0.05)