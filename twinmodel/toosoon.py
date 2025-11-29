import numpy as np
import matplotlib.pyplot as plt

def calculate_memory_gain(time_since_last_review, optimal_interval):
    """
    Calculates how much 'strength' you gain from a review based on TIMING.
    
    This uses a skewed bell curve logic.
    - If you review instantly (time=0), gain is near 0 (The Lag Effect).
    - If you review at optimal_interval, gain is 1.0 (Max).
    - If you wait too long, gain drops (Recall failed).
    """
    
    # We use a normalized time ratio: t / optimal
    ratio = time_since_last_review / optimal_interval
    
    # Logic: 
    # 1. If ratio is small (< 0.2), gain is tiny (Cramming Penalty).
    # 2. As ratio approaches 1.0, gain peaks.
    # 3. If ratio > 1.5, gain drops (Forgetting).
    
    # A simplified mathematical model for this curve:
    # gain = ratio * exp(1 - ratio)
    gain = ratio * np.exp(1 - ratio)
    
    return gain

# --- VISUALIZATION ---
# Let's say the optimal time to review "Card A" is 10 days from now.
optimal_interval = 10 
days_passed = np.linspace(0, 25, 100)

gains = [calculate_memory_gain(t, optimal_interval) for t in days_passed]

plt.figure(figsize=(10, 5))
plt.plot(days_passed, gains, color='purple', linewidth=3)

# Add annotations
plt.axvline(x=optimal_interval, color='green', linestyle='--', label='Sweet Spot (10 Days)')
plt.text(0.5, 0.2, "Zone 1: Cramming\n(Zero Value)", color='red', fontsize=12)
plt.text(10.5, 0.9, "Zone 2: Max Learning", color='green', fontsize=12)
plt.text(18, 0.4, "Zone 3: Forgot", color='gray', fontsize=12)

plt.title("The Lag Effect: Why Cramming Fails")
plt.xlabel("Days Since Last Review")
plt.ylabel("Memory Strength Gained")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()