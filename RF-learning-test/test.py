import os
import json
import numpy as np

# File where Q-values (preferences) will be saved
Q_VALUES_FILE = 'q_values.json'

# Load Q-values from the file if it exists
def load_q_values():
    if os.path.exists(Q_VALUES_FILE):
        with open(Q_VALUES_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save Q-values to the file
def save_q_values(q_values):
    with open(Q_VALUES_FILE, 'w') as file:
        json.dump(q_values, file)

# Initialize Q-values for a new number if it doesn't exist
def initialize_q_value(q_values, number):
    if number not in q_values:
        q_values[number] = 0  # Initial preference (Q-value) is 0
    return q_values

# Q-learning update rule
def update_q_value(q_values, number, reward, alpha=0.1):
    # Update the Q-value for the number with the reward
    q_values[number] = q_values[number] + alpha * (reward - q_values[number])
    return q_values

# Function to show preferred numbers based on Q-values
def show_preferred_numbers(q_values):
    if q_values:
        # Sort numbers by preference (Q-value)
        preferred_numbers = sorted(q_values.items(), key=lambda x: x[1], reverse=True)
        print("Your preferred numbers (sorted by preference):", preferred_numbers)
    else:
        print("You have no preferred numbers yet.")

# Function to add a new number and update Q-value
def add_number(q_values, number, reward=1):
    q_values = initialize_q_value(q_values, number)
    q_values = update_q_value(q_values, number, reward)
    print(f"{number} added/updated with a reward of {reward}.")
    return q_values

# Main function to interact with the user using reinforcement learning
def main():
    # Load Q-values (preferences) from the file
    q_values = load_q_values()

    print("Welcome! You can add your preferred numbers.")
    print("Type 'add' to add a new number, 'show' to see the preferred list, and 'exit' to quit the program.")

    while True:
        command = input("\nEnter a command (add/show/exit): ").strip().lower()

        if command == "add":
            try:
                number = int(input("Enter a number: "))
                # Reward is positive for each time user enters the number
                q_values = add_number(q_values, number, reward=1)
            except ValueError:
                print("Please enter a valid number.")

        elif command == "show":
            show_preferred_numbers(q_values)

        elif command == "exit":
            save_q_values(q_values)
            print("Exiting and saving your preferences. Goodbye!")
            break

        else:
            print("Invalid command. Please use 'add', 'show', or 'exit'.")

if __name__ == "__main__":
    main()
