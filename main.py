import json
import os
from datetime import datetime

# Define the file name where data will persist
DATA_FILE = "expenses.json"

def load_expenses():
    """Loads expenses from the JSON file. Returns an empty list if file doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        # Fallback if file is corrupted
        return []

def save_expenses(expenses):
    """Saves the expenses list back to the JSON file to persist data."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(expenses, file, indent=4)
    except IOError:
        print("\nError: Could not save data to disk.")

def get_validated_amount():
    """Strictly validates amount against empty or negative inputs."""
    while True:
        val = input("Enter amount: ").strip()
        if not val:
            print("Error: Amount cannot be empty. Please enter a valid number.")
            continue
        try:
            amount = float(val)
            if amount <= 0:
                print("Error: Amount must be a positive number greater than 0.")
                continue
            return round(amount, 2)
        except ValueError:
            print("Error: Invalid input. Please enter a numeric value (e.g., 10.50).")

def get_validated_date():
    """Strictly validates date formatting to prevent weird or broken dates."""
    while True:
        date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date_str:
            return datetime.today().strftime('%Y-%m-%d')
        try:
            # Validates if the string matches the exact ISO pattern and is a real date
            valid_date = datetime.strptime(date_str, "%Y-%m-%d")
            return valid_date.strftime('%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date or format. Please use exactly YYYY-MM-DD (e.g., 2026-07-25).")

def print_table(expenses):
    """Displays expenses cleanly in a strict terminal table format."""
    if not expenses:
        print("\nNo expenses found matching the criteria.")
        return

    # FIXED: Added the specific pixel padding column widths for each table layout item
    headers = ["ID", "Amount ($)", "Category", "Date", "Note"]
    col_widths = [4, 12, 15, 12, 25]
    
    # Create the separator row line
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    # Header row printing
    header_row = "|" + "|".join(f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers))) + "|"
    print(header_row)
    print(separator)
    
    # Body rows printing
    total_spent = 0.0
    for idx, exp in enumerate(expenses, start=1):
        amount = exp["amount"]
        total_spent += amount
        
        row = [
            str(idx),
            f"{amount:.2f}",
            exp["category"],
            exp["date"],
            exp["note"]
        ]
        
        row_str = "|" + "|".join(f" {row[i].ljust(col_widths[i])} " for i in range(len(row))) + "|"
        print(row_str)
        
    print(separator)
    print(f"TOTAL SPENT MATCHING CRITERIA: ${total_spent:.2f}")

def add_expense_flow(expenses):
    """Executes the user workflow to append a new expense."""
    print("\n--- Add New Expense ---")
    amount = get_validated_amount()
    
    category = input("Enter category (e.g., Food, Transport, Rent): ").strip()
    while not category:
        print("Error: Category cannot be empty.")
        category = input("Enter category: ").strip()
        
    date = get_validated_date()
    
    note = input("Enter note / description: ").strip()
    if not note:
        note = "N/A"
        
    # Append data structure strictly meeting specifications
    new_expense = {
        "amount": amount,
        "category": category.capitalize(),
        "date": date,
        "note": note
    }
    
    expenses.append(new_expense)
    save_expenses(expenses)
    print("\nExpense added successfully and saved!")

def filter_expenses_flow(expenses):
    """Filters expenses by category and prints summary breakdown data."""
    print("\n--- View & Filter Expenses ---")
    if not expenses:
        print("Your expense database is currently empty.")
        return
        
    # Calculate overall absolute total first
    overall_total = sum(e["amount"] for e in expenses)
    print(f"📊 Overall Total Spent Across All Records: ${overall_total:.2f}")
    
    # Gather distinct existing categories
    categories = sorted(list(set(e["category"] for e in expenses)))
    print(f"Available categories: {', '.join(categories)}")
    
    choice = input("Enter a specific category to filter by (or press Enter to view all): ").strip().capitalize()
    
    if choice:
        filtered = [e for e in expenses if e["category"] == choice]
        print_table(filtered)
    else:
        print_table(expenses)

def main():
    expenses = load_expenses()
    
    while True:
        print("\n==============================")
        print("   PERSONAL EXPENSE TRACKER   ")
        print("==============================")
        print("1. Add Expense")
        print("2. View & Filter Expenses")
        print("3. Exit Application")
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == "1":
            add_expense_flow(expenses)
        elif choice == "2":
            filter_expenses_flow(expenses)
        elif choice == "3":
            print("\nExiting application. All data is safe in expenses.json.")
            break
        else:
            print("\nInvalid option. Please input 1, 2, or 3.")

if __name__ == "__main__":
    main()
