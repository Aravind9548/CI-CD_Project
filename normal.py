import json
from datetime import datetime

DATABASE_FILE = 'calculations.json'

def load_data():
    """Loads the calculation history from a JSON file."""
    try:
        with open(DATABASE_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, return an empty list.
        return []

def save_data(data):
    """Saves the calculation history to a JSON file."""
    with open(DATABASE_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def calculate(num1, num2, operator):
    """Performs a simple calculation and returns the result."""
    if operator == '+':
        return num1 + num2
    elif operator == '-':
        return num1 - num2
    elif operator == '*':
        return num1 * num2
    elif operator == '/':
        if num2 == 0:
            print("Error: Cannot divide by zero.")
            return None
        return num1 / num2
    else:
        print("Error: Invalid operator.")
        return None

def main():
    """Main function to run the calculator and history storage."""
    try:
        # Get user input for the calculation
        num1 = float(input("Enter first number: "))
        operator = input("Enter operator (+, -, *, /): ")
        num2 = float(input("Enter second number: "))

        # Perform the calculation
        result = calculate(num1, num2, operator)

        if result is not None:
            print(f"Result: {result}")
            
            # Load existing history from the file
            history = load_data()
            
            # Create a new history entry
            new_entry = {
                'calculation': f"{num1} {operator} {num2}",
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add the new entry to the history
            history.append(new_entry)
            
            # Save the updated history back to the file
            save_data(history)
            
            print("Calculation saved to history.")
            
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        
    print("\n--- Calculation History ---")
    history = load_data()
    if history:
        for entry in history:
            print(f"{entry['calculation']} = {entry['result']} ({entry['timestamp']})")
    else:
        print("No history found.")

if __name__ == "__main__":
    main()