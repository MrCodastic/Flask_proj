import pandas as pd
import datetime

class AnkiCard:
    def __init__(self, topic, front, back):
        self.topic = topic
        self.front = front
        self.back = back
        
        # --- THE MEMORY MODEL STATE ---
        self.repetition_number = 0  # How many times reviewed?
        self.interval = 1           # Days until next review
        self.ease_factor = 2.5      # "Stickiness" of the memory (Standard start is 2.5)
        self.last_review_date = datetime.date.today()
        self.next_review_date = datetime.date.today()

    def review(self, user_grade):
        """
        user_grade: 
        0 = Blackout (Forgot completely)
        3 = Pass (Hard but remembered)
        4 = Good (Remembered with hesitation)
        5 = Perfect (Instant recall)
        """
        self.last_review_date = datetime.date.today()
        
        if user_grade < 3:
            # PENALTY: You forgot! Reset everything.
            self.repetition_number = 0
            self.interval = 1
            # We don't change Ease Factor much on failure, just reset the streak
        else:
            # SUCCESS: Update the model
            
            # 1. Update Ease Factor (The Complex Math Part of SM-2)
            # This formula adjusts how "hard" the card is based on your grade.
            # If Grade is 5, EF goes UP. If Grade is 3, EF goes DOWN.
            self.ease_factor = self.ease_factor + (0.1 - (5 - user_grade) * (0.08 + (5 - user_grade) * 0.02))
            
            # Cap the Ease Factor (Standard constraint: never drop below 1.3)
            if self.ease_factor < 1.3:
                self.ease_factor = 1.3
            
            # 2. Calculate Next Interval
            if self.repetition_number == 0:
                self.interval = 1
            elif self.repetition_number == 1:
                self.interval = 6
            else:
                # EXPONENTIAL GROWTH
                self.interval = int(self.interval * self.ease_factor)
            
            self.repetition_number += 1

        # Calculate the actual date
        self.next_review_date = datetime.date.today() + datetime.timedelta(days=self.interval)
        
        return self.interval, self.ease_factor

# --- SIMULATION ---
# Let's simulate a user learning the word "Digital Twin" over a few months

card = AnkiCard("Tech", "Digital Twin", "Virtual Model of Physical System")

print(f"--- STARTING LEARNING: {card.front} ---")
print(f"Initial Ease Factor: {card.ease_factor}")

# Scenario: The user struggles at first, then masters it.
simulated_reviews = [
    3, # Day 0: "Pass" (Hard)
    4, # Next review: "Good"
    5, # Next review: "Perfect"
    5, # Next review: "Perfect"
    5  # Next review: "Perfect"
]

history = []

for grade in simulated_reviews:
    # Perform review
    days_jump, new_ef = card.review(grade)
    
    # Store data
    history.append({
        "User Grade": grade,
        "Next Interval (Days)": days_jump,
        "New Ease Factor": round(new_ef, 3),
        "Next Review Date": card.next_review_date
    })

# Display Results
df = pd.DataFrame(history)
print(df)