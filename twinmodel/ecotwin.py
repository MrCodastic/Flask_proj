import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="Economic Policy Twin", layout="wide")
st.title("💰 Economic Development Twin")
st.markdown("""
**Simulate a National Economy.**
Agents (Citizens) interact with Firms. You are the **Central Bank & Government**.
* **Goal:** High GDP, Low Inequality (Gini).
""")

# --- 1. CONFIGURATION (The Policy Levers) ---
st.sidebar.header("Fiscal & Monetary Policy")

tax_rate = st.sidebar.slider("Income Tax Rate (%)", 0, 50, 10, help="Money taken from agents each step.")
stimulus_check = st.sidebar.number_input("Stimulus Check Amount ($)", 0, 500, 0, help="Free money given to everyone per step.")
min_wage = st.sidebar.slider("Minimum Wage ($)", 10, 50, 20)

st.sidebar.header("Simulation Settings")
num_agents = 100
num_firms = 10
steps = st.sidebar.slider("Simulation Duration (Months)", 10, 100, 50)

# --- 2. THE ECONOMIC AGENTS ---

class Agent:
    def __init__(self, id):
        self.id = id
        self.money = 100 # Initial savings
        self.employed = False
        
    def buy_goods(self, price):
        # Logic: Agents must spend to survive. 
        # If they have excess money, they spend more (propensity to consume).
        spend_amount = 0
        if self.money >= price:
            self.money -= price
            spend_amount = price
        return spend_amount

class Firm:
    def __init__(self, id):
        self.id = id
        self.capital = 1000
        self.employees = 0
        self.price = 20 # Initial price of goods
        self.inventory = 10
    
    def pay_wages(self, wage):
        # Firms pay employees
        total_wages = self.employees * wage
        if self.capital >= total_wages:
            self.capital -= total_wages
            return wage # Successful payment
        else:
            return 0 # Bankruptcy / Layoff risk

# --- 3. THE TWIN ENGINE ---

def run_economy():
    # Initialize Population
    agents = [Agent(i) for i in range(num_agents)]
    firms = [Firm(i) for i in range(num_firms)]
    
    # Randomly assign employment
    for agent in agents:
        agent.employer = random.choice(firms)
        agent.employer.employees += 1

    history = {
        'step': [], 'gdp': [], 'avg_wealth': [], 
        'inflation': [], 'inequality': []
    }
    
    current_price = 20 # Starting price level
    
    for step in range(steps):
        step_gdp = 0
        total_demand = 0
        total_supply = 0
        
        # --- A. PRODUCTION & WAGES PHASE ---
        for firm in firms:
            # Firm produces goods based on workforce
            firm.inventory += firm.employees * 2 
            total_supply += firm.inventory
            
            # Firm pays wages
            wage_paid = firm.pay_wages(min_wage)
            
            # Distribute wages to employees
            for agent in agents:
                if agent.employer == firm:
                    # Apply Tax
                    net_income = wage_paid * (1 - (tax_rate/100))
                    agent.money += net_income + stimulus_check # Add Stimulus
        
        # --- B. CONSUMPTION PHASE ---
        for agent in agents:
            # Agents try to buy goods
            spent = agent.buy_goods(current_price)
            if spent > 0:
                step_gdp += spent
                total_demand += 1
                
                # Money goes to random firm (Simplified market)
                seller = random.choice(firms)
                seller.capital += spent
                seller.inventory -= 1

        # --- C. MARKET DYNAMICS (The "Invisible Hand") ---
        # Adjust Price based on Supply vs Demand
        # If Demand > Supply, Prices rise (Inflation)
        if total_demand > total_supply * 0.8: 
            current_price *= 1.05 # +5% Inflation
        elif total_demand < total_supply * 0.4:
            current_price *= 0.95 # -5% Deflation (Sale)
            
        # --- D. DATA RECORDING ---
        wealths = [a.money for a in agents]
        avg_wealth = sum(wealths) / len(agents)
        
        # Calculate Gini Coefficient (Inequality)
        # 0 = Perfect Equality, 1 = Perfect Inequality
        wealths_sorted = sorted(wealths)
        n = len(agents)
        coef = 2.0 / n
        const = (n + 1.0) / n
        weighted_sum = sum([(i+1)*y for i, y in enumerate(wealths_sorted)])
        gini = (coef * weighted_sum / (sum(wealths_sorted) + 0.0001)) - const
        
        history['step'].append(step)
        history['gdp'].append(step_gdp)
        history['avg_wealth'].append(avg_wealth)
        history['inflation'].append(current_price)
        history['inequality'].append(gini)

    return pd.DataFrame(history)

# --- 4. RUN & VISUALIZE ---
if st.button("🚀 Run Simulation"):
    df = run_economy()
    
    # METRICS
    final_gdp = df['gdp'].iloc[-1]
    final_inf = df['inflation'].iloc[-1]
    final_gini = df['inequality'].iloc[-1]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Final GDP (Spending)", f"${int(final_gdp)}")
    c2.metric("Price Index (Inflation)", f"${int(final_inf)}")
    c3.metric("Inequality (Gini)", f"{final_gini:.2f}")
    
    # CHARTS
    st.subheader("Economic Indicators Over Time")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**GDP & Wealth**")
        fig1, ax1 = plt.subplots()
        ax1.plot(df['step'], df['gdp'], label='GDP', color='green')
        ax1.plot(df['step'], df['avg_wealth'], label='Avg Citizen Wealth', color='blue', linestyle='--')
        ax1.legend()
        ax1.set_title("Growth vs Wealth")
        st.pyplot(fig1)

    with col2:
        st.write("**Inflation & Inequality**")
        fig2, ax2 = plt.subplots()
        ax2.plot(df['step'], df['inflation'], label='Price of Bread', color='red')
        ax2.set_ylabel("Price ($)", color='red')
        
        ax3 = ax2.twinx()
        ax3.plot(df['step'], df['inequality'], label='Inequality (Gini)', color='purple', linestyle='-.')
        ax3.set_ylabel("Gini Index (0-1)", color='purple')
        ax3.set_ylim(0, 1)
        
        fig2.legend(loc="upper left")
        st.pyplot(fig2)
        
    # ANALYSIS
    st.write("### Simulation Analysis")
    if final_inf > 100:
        st.error("🚨 **Hyperinflation Crisis:** Prices skyrocketed! You likely printed too much money (Stimulus) without increasing production.")
    elif final_gini > 0.6:
        st.warning("⚠️ **Inequality Alert:** The rich own everything. The economy might collapse due to lack of demand from workers.")
    elif final_gdp < 1000:
        st.warning("📉 **Recession:** Economic activity has halted. Try lowering taxes or increasing wages.")
    else:
        st.success("✅ **Stable Economy:** Good balance of growth and stability.")