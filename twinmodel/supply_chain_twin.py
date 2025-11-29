import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
st.set_page_config(page_title="Supply Chain Digital Twin", layout="wide")

st.title("📦 Supply Chain Digital Twin: Inventory Optimizer")
st.markdown("""
This Twin simulates a **Retail Warehouse**. 
You must balance **Customer Demand** (unpredictable) with **Supplier Lead Time** (slow).
""")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Warehouse Parameters")

# 1. The Policy (The "Brain" of the Twin)
reorder_point = st.sidebar.slider("Reorder Point (When to buy?)", 10, 200, 50)
order_qty = st.sidebar.slider("Reorder Quantity (How much?)", 10, 200, 100)

# 2. The External World (The Chaos)
lead_time = st.sidebar.slider("Supplier Delay (Days)", 1, 10, 3)
demand_volatility = st.sidebar.slider("Customer Panic (Volatility)", 0.0, 1.0, 0.2)
initial_stock = 200

# --- SIMULATION ENGINE ---
def run_supply_chain_sim(days=100):
    # State Variables
    inventory = initial_stock
    pending_orders = [] # List of (arrival_day, quantity)
    
    # History for plotting
    history = {
        'day': [], 
        'inventory': [], 
        'demand': [], 
        'stockout': []
    }
    
    # Run Simulation Day by Day
    for day in range(days):
        # 1. Receive incoming shipments
        # Check if any order arrives today
        arrived_stock = 0
        remaining_orders = []
        for delivery_day, qty in pending_orders:
            if day >= delivery_day:
                arrived_stock += qty
            else:
                remaining_orders.append((delivery_day, qty))
        pending_orders = remaining_orders
        inventory += arrived_stock
        
        # 2. Customer Demand (Randomized)
        # Base demand is 20, plus volatility spike
        daily_demand = int(np.random.normal(20, 20 * demand_volatility))
        if daily_demand < 0: daily_demand = 0
        
        # 3. Fulfill Orders
        if inventory >= daily_demand:
            inventory -= daily_demand
            stockout = 0
        else:
            # We ran out! 
            stockout = daily_demand - inventory
            inventory = 0
        
        # 4. Inventory Check (The Logic)
        # If stock is low, place an order
        if inventory < reorder_point:
            # Only order if we don't have too many already coming? 
            # (Simple Logic: Just order blindly)
            arrival_day = day + lead_time
            pending_orders.append((arrival_day, order_qty))
            
        # 5. Record Data
        history['day'].append(day)
        history['inventory'].append(inventory)
        history['demand'].append(daily_demand)
        history['stockout'].append(stockout)
        
    return pd.DataFrame(history)

# --- RUN BUTTON ---
if st.button("🔄 Run Simulation"):
    df = run_supply_chain_sim()
    
    # --- METRICS ---
    total_stockouts = df['stockout'].sum()
    avg_inventory = df['inventory'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Lost Sales (Units)", f"{total_stockouts}", delta_color="inverse")
    col2.metric("Avg Inventory Level", f"{avg_inventory:.1f}")
    col3.metric("Survival Rate", f"{100 - (len(df[df['inventory']==0])/len(df)*100):.1f}%")

    # --- VISUALIZATION ---
    st.subheader("Inventory Levels Over Time")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plot Inventory Area
    ax.fill_between(df['day'], df['inventory'], color='skyblue', alpha=0.4, label='Stock Level')
    ax.plot(df['day'], df['inventory'], color='blue')
    
    # Plot Reorder Line
    ax.axhline(y=reorder_point, color='green', linestyle='--', label=f'Reorder Point ({reorder_point})')
    
    # Plot Stockouts (Red bars)
    stockout_days = df[df['stockout'] > 0]
    ax.bar(stockout_days['day'], stockout_days['stockout'], color='red', label='Missed Sales (Stockout)')
    
    ax.set_ylabel("Units")
    ax.set_xlabel("Day")
    ax.legend()
    
    st.pyplot(fig)
    
    st.write("### What happened?")
    if total_stockouts > 50:
        st.error(f"❌ **CRITICAL FAILURE:** You lost {total_stockouts} sales. Your reorder point might be too low, or your supplier is too slow.")
    elif avg_inventory > 400:
        st.warning(f"⚠️ **OVERSTOCK:** You are paying too much for storage. Try lowering your reorder quantity.")
    else:
        st.success("✅ **OPTIMAL:** Good balance between sales and stock costs.")