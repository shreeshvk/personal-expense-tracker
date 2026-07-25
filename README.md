# personal-expense-tracker

A Python Command Line Interface (CLI) application built to track, organize, and summarize personal financial expenses cleanly directly inside the terminal.

## Key Functional Features

- **Strict Input Validation Engine:** Protects the application database against crashing from empty strings, negative numerical costs, invalid characters, or non-existent calendar dates (e.g., 2026-02-30).
- **Structured Data Persistence:** Dynamically saves and loads transactions to an independent `expenses.json` file storage ledger so data survives system restarts.
- **ASCII Grid Table Formatting:** Formats and prints logged transaction variables cleanly into a structured tabular grid schema inside the shell environment.
- **Category Matrix Summarization:** Summarizes absolute global expenditure totals alongside dynamic filtered subgroup pricing tallies based on custom categories (e.g., Food, Subscriptions, Transport).

## Getting Started on Linux

### Prerequisites
Ensure you have Python 3 installed on your local operating system:
```bash
python3 --version
```

### Execution Instructions
To launch the interactive terminal interface tracking hub, navigate to the source directory and execute the main entry script:
```bash
python3 main.py
```

## Grading Presentation Bug Notes
*(Documented for the 10-minute presentation stress-test criteria)*
- **Resolved Bug Encountered:** During initial structural compilation, the table formatting component suffered a layout execution hazard where missing custom character index dimension values (`col_widths`) caused index matching calculation loops to break. 
- **Technical Correction Implementation:** Resolved the calculation hazard by explicitly locking static maximum padding column widths (`[4, 12, 15, 12, 30]`) to gracefully map strings to dynamic cell spacing.