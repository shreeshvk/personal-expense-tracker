import json
import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# Define the file name where data will persist
DATA_FILE = "expenses.json"

def load_expenses():
#Loads expenses from the JSON file.
#Returns: A list of expense dictionaries. If the file doesn't exist or is corrupted,an empty list is returned.
#Converts stored amount values into Decimal objects for accurate financial calculations.

    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as file:
            expenses = json.load(file)
        # Convert stored amounts to Decimal
        for expense in expenses:
            expense["amount"] = Decimal(str(expense["amount"])).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
        return expenses
    except (json.JSONDecodeError, IOError, KeyError, ValueError):
        # Return an empty list if the file is corrupted or contains invalid data
        return []

def save_expenses(expenses):
    # Saves the expenses list to the JSON file.
    # Converts Decimal amounts to float before saving.

    try:
        save_data = []
        for expense in expenses:
            save_data.append({
                "amount": float(expense["amount"]),
                "category": expense["category"],
                "date": expense["date"],
                "note": expense["note"]
            })
        with open(DATA_FILE, "w") as file:
            json.dump(save_data, file, indent=4)
    except IOError:
        print("\nError: Could not save data to disk.")

def get_validated_amount():
    # Validates amount input.
    # Ensures the value is numeric and greater than 0.
    # Returns a Decimal rounded to 2 decimal places.

    while True:
        val = input("Enter amount: ").strip()
        if not val:
            print("Error: Amount cannot be empty. Please enter a valid number.")
            continue
        try:
            amount = Decimal(val).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP
            )
            if amount <= Decimal("0.00"):
                print("Error: Amount must be a positive number greater than 0.")
                continue
            return amount
        except:
            print("Error: Invalid input. Please enter a numeric value (e.g., 10.50).")

def get_validated_date():
    # Strictly validates date formatting to prevent invalid dates.
    while True:
        date_str = input("Enter date (DD-MM-YYYY) or press Enter for today: ").strip()
        if not date_str:
            return datetime.today().strftime("%d-%m-%Y")
        try:
            # Validates if the string matches the exact format and is a real date
            valid_date = datetime.strptime(date_str, "%d-%m-%Y")
            return valid_date.strftime("%d-%m-%Y")
        except ValueError:
            print("Error: Invalid date or format. Please use exactly DD-MM-YYYY (e.g., 25-07-2026).")

def print_table(expenses):
    # Displays expenses in a formatted table.
    # Truncates long notes for better readability.

    if not expenses:
        print("\nNo expenses found matching the criteria.")
        return
    headers = ["ID", "Amount (RM)", "Category", "Date", "Note"]
    col_widths = [4, 12, 15, 12, 25]
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "|" + "|".join(
        f" {headers[i].ljust(col_widths[i])} "
        for i in range(len(headers))
    ) + "|"
    print(separator)
    print(header_row)
    print(separator)
    total_spent = Decimal("0.00")
    for idx, exp in enumerate(expenses, start=1):
        amount = exp["amount"]
        total_spent += amount
        # Truncate long notes
        note = exp["note"]
        if len(note) > 22:
            note = note[:19] + "..."
        row = [
            str(idx),
            f"{amount:.2f}",
            exp["category"],
            exp["date"],
            note
        ]
        row_str = "|" + "|".join(
            f" {row[i].ljust(col_widths[i])} "
            for i in range(len(row))
        ) + "|"
        print(row_str)
    print(separator)
    print(f"TOTAL SPENT MATCHING CRITERIA: RM{total_spent:.2f}")

def add_expense_flow(expenses):
    # Allows the user to add one or more expenses in a single session.

    while True:
        print("\n--- Add New Expense ---")
        amount = get_validated_amount()
        # Display existing categories
        categories = sorted(set(expense["category"] for expense in expenses))
        if categories:
            print(f"Existing categories: {', '.join(categories)}")
        category = input("Enter category (e.g., Food, Transport, Rent): ").strip()
        while not category:
            print("Error: Category cannot be empty.")
            category = input("Enter category: ").strip()
        date = get_validated_date()
        note = input("Enter note / description: ").strip()
        if not note:
            note = "N/A"
        # Append the new expense
        new_expense = {
            "amount": amount,
            "category": category.capitalize(),
            "date": date,
            "note": note
        }
        expenses.append(new_expense)
        save_expenses(expenses)
        print("\nExpense added successfully and saved!")
        # Ask if the user wants to add another expense
        choice = input("\nAdd another expense? (Y/N): ").strip().upper()
        while choice not in ["Y", "N"]:
            print("Error: Please enter Y or N.")
            choice = input("Add another expense? (Y/N): ").strip().upper()
        if choice == "N":
            break

def filter_expenses_flow(expenses):
    # Filters expenses by one or more categories.
    # Allows sorting by date, amount, or category.

    print("\n--- View & Filter Expenses ---")
    if not expenses:
        print("Your expense database is currently empty.")
        return
    # Calculate overall total
    overall_total = sum(e["amount"] for e in expenses)
    print(f"Overall Total Spent Across All Records: RM{overall_total:.2f}")
    # Display available categories
    categories = sorted(set(e["category"] for e in expenses))
    print(f"Available categories: {', '.join(categories)}")
    choice = input(
        "\nEnter category/categories to filter by "
        "(separate multiple categories with commas, or press Enter to view all): "
    ).strip()
    if choice:
        selected_categories = [
            category.strip().capitalize()
            for category in choice.split(",")
        ]
        filtered = [
            expense
            for expense in expenses
            if expense["category"] in selected_categories
        ]
    else:
        filtered = expenses
    # Sorting options
    print("\nSort options:")
    print("1. Date")
    print("2. Amount")
    print("3. Category")
    print("4. No sorting")
    sort_choice = input("Choose sorting option (1-4): ").strip()
    if sort_choice == "1":
        filtered.sort(
            key=lambda expense: datetime.strptime(
                expense["date"],
                "%d-%m-%Y"
            )
        )
    elif sort_choice == "2":
        filtered.sort(
            key=lambda expense: expense["amount"]
        )
    elif sort_choice == "3":
        filtered.sort(
            key=lambda expense: expense["category"]
        )
    elif sort_choice != "4":
        print("Invalid sorting option. Displaying without sorting.")
    print_table(filtered)

def edit_expense_flow(expenses):
    # Allows the user to edit an existing expense.
    # Requires confirmation before saving changes.

    if not expenses:
        print("\nNo expenses available to edit.")
        return
    print_table(expenses)
    try:
        expense_id = int(input("\nEnter expense ID to edit: "))
        if expense_id < 1 or expense_id > len(expenses):
            print("Invalid expense ID.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    expense = expenses[expense_id - 1]
    print("\nCurrent expense details:")
    print(f"Amount: RM{expense['amount']}")
    print(f"Category: {expense['category']}")
    print(f"Date: {expense['date']}")
    print(f"Note: {expense['note']}")
    confirm = input("\nEdit this expense? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("Edit cancelled.")
        return
    print("\nEnter new details:")
    expense["amount"] = get_validated_amount()
    category = input("Enter category: ").strip()
    while not category:
        print("Error: Category cannot be empty.")
        category = input("Enter category: ").strip()
    expense["category"] = category.capitalize()
    expense["date"] = get_validated_date()
    note = input("Enter note / description: ").strip()
    if not note:
        note = "N/A"
    expense["note"] = note

    save_expenses(expenses)

    print("\nExpense updated successfully!")

def delete_expense_flow(expenses):
    # Deletes an expense after user confirmation.

    if not expenses:
        print("\nNo expenses available to delete.")
        return
    print_table(expenses)
    try:
        expense_id = int(input("\nEnter expense ID to delete: "))
        if expense_id < 1 or expense_id > len(expenses):
            print("Invalid expense ID.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    expense = expenses[expense_id - 1]
    print("\nSelected expense:")
    print(f"RM{expense['amount']} - {expense['category']} - {expense['note']}")
    confirm = input("\nAre you sure you want to delete this expense? (Y/N): ")
    if confirm.strip().upper() == "Y":
        expenses.pop(expense_id - 1)
        save_expenses(expenses)
        print("\nExpense deleted successfully!")
    else:
        print("\nDelete cancelled.")

def category_summary(expenses):
    # Displays total spending grouped by category.

    if not expenses:
        print("\nNo expenses available.")
        return
    summary = {}
    for expense in expenses:
        category = expense["category"]
        summary[category] = (
            summary.get(category, Decimal("0.00"))
            + expense["amount"]
        )
    print("\n--- Category Spending Summary ---")
    for category, total in sorted(summary.items()):
        print(f"{category}: RM{total:.2f}")

def statistics(expenses):
    # Displays overall expense statistics.

    if not expenses:
        print("\nNo expenses available.")
        return
    amounts = [
        expense["amount"]
        for expense in expenses
    ]
    total = sum(
        amounts,
        Decimal("0.00")
    )
    average = (
        total / len(amounts)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
    highest = max(amounts)
    lowest = min(amounts)
    print("\n--- Overall Statistics ---")
    print(f"Total Spent: RM{total:.2f}")
    print(f"Average Expense: RM{average:.2f}")
    print(f"Highest Expense: RM{highest:.2f}")
    print(f"Lowest Expense: RM{lowest:.2f}")
    print(f"Number of Expenses: {len(expenses)}")

def clear_expenses():
    # Clears all expense records from the JSON file.

    with open(DATA_FILE, "w") as file:
        json.dump([], file, indent=4)

    print("\nAll expenses have been cleared.")

def main():
    # Loads existing expenses and runs the main menu.

    expenses = load_expenses()

    while True:
        print("\n==============================")
        print("   PERSONAL EXPENSE TRACKER   ")
        print("==============================")
        print("1. Add Expense")
        print("2. View & Filter Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Category Spending Summary")
        print("6. Overall Statistics")
        print("7. Exit Application")
        print("8. Clear All Expenses")

        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            add_expense_flow(expenses)
        elif choice == "2":
            filter_expenses_flow(expenses)
        elif choice == "3":
            edit_expense_flow(expenses)
        elif choice == "4":
            delete_expense_flow(expenses)
        elif choice == "5":
            category_summary(expenses)
        elif choice == "6":
            statistics(expenses)
        elif choice == "7":
            print("\nExiting application. All data is safe in expenses.json.")
        elif choice == "8":
            clear_expenses()
            break
        else:
            print("\nInvalid option. Please input a number between 1 and 8.")

if __name__ == "__main__":
    main()