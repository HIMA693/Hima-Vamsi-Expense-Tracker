import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import html
import webbrowser
from pathlib import Path
from datetime import date, datetime

# ============================================================
# HIMA VAMSI EXPENSE TRACKER V2.0
# Uses Python standard library only. Keeps the existing database.
# ============================================================

# DATABASE: Keep this file in the same folder as main.py.
conn = sqlite3.connect("expense_tracker.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    transaction_date TEXT NOT NULL
)
""")
conn.commit()

editing_id = None

# COLORS
BG = "#080D18"
PANEL = "#111A2B"
CARD = "#17263D"
CYAN = "#20D6E8"
WHITE = "#FFFFFF"
MUTED = "#91A1B9"
GREEN = "#22C55E"
RED = "#F87171"
YELLOW = "#FACC15"

# MAIN WINDOW
root = tk.Tk()
root.title("Hima Vamsi Expense Tracker V2.0")
root.geometry("1250x850")
root.minsize(1050, 700)
root.configure(bg=BG)

# THEME
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    background=PANEL,
    foreground=WHITE,
    fieldbackground=PANEL,
    rowheight=32,
    font=("Arial", 10)
)
style.configure(
    "Treeview.Heading",
    background=CARD,
    foreground=CYAN,
    font=("Arial", 10, "bold"),
    padding=8
)
style.map(
    "Treeview",
    background=[("selected", "#24516A")],
    foreground=[("selected", WHITE)]
)
style.configure("TCombobox", fieldbackground=CARD, padding=6)

# HEADER
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=25, pady=15)

tk.Label(
    header, text="HV", font=("Arial", 22, "bold"),
    bg=CYAN, fg=BG, width=4, height=2
).pack(side="left", padx=(0, 15))

title_area = tk.Frame(header, bg=BG)
title_area.pack(side="left")

tk.Label(
    title_area, text="HIMA VAMSI",
    font=("Arial", 22, "bold"), fg=WHITE, bg=BG
).pack(anchor="w")

tk.Label(
    title_area, text="PERSONAL FINANCE MANAGEMENT | V2.0",
    font=("Arial", 10, "bold"), fg=CYAN, bg=BG
).pack(anchor="w")

# DASHBOARD
dashboard = tk.Frame(root, bg=BG)
dashboard.pack(fill="x", padx=25, pady=8)

def create_card(parent, heading, color):
    card = tk.Frame(
        parent, bg=CARD,
        highlightbackground="#263B58", highlightthickness=1
    )
    tk.Label(
        card, text=heading, font=("Arial", 10, "bold"),
        bg=CARD, fg=MUTED
    ).pack(anchor="w", padx=18, pady=(12, 5))
    value_label = tk.Label(
        card, text="₹0.00", font=("Arial", 21, "bold"),
        bg=CARD, fg=color
    )
    value_label.pack(anchor="w", padx=18, pady=(0, 12))
    return card, value_label

balance_card, balance_label = create_card(dashboard, "TOTAL BALANCE", CYAN)
income_card, income_label = create_card(dashboard, "TOTAL INCOME", GREEN)
expense_card, expense_label = create_card(dashboard, "TOTAL EXPENSES", RED)

for card in (balance_card, income_card, expense_card):
    card.pack(side="left", fill="both", expand=True, padx=6)

# MAIN CONTENT
content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True, padx=25, pady=8)

# TRANSACTION FORM
form = tk.Frame(
    content, bg=PANEL,
    highlightbackground="#263B58", highlightthickness=1
)
form.pack(fill="x", pady=(0, 8))

form_title = tk.Label(
    form, text="ADD NEW TRANSACTION",
    font=("Arial", 13, "bold"), bg=PANEL, fg=CYAN
)
form_title.grid(row=0, column=0, columnspan=4,
                sticky="w", padx=15, pady=10)

def create_label(parent, text, row, column):
    tk.Label(
        parent, text=text, font=("Arial", 9, "bold"),
        bg=PANEL, fg=WHITE
    ).grid(row=row, column=column, sticky="w", padx=15, pady=(5, 3))

def create_entry(parent, row, column):
    entry = tk.Entry(
        parent, font=("Arial", 10), bg=CARD, fg=WHITE,
        insertbackground=WHITE, relief="flat"
    )
    entry.grid(row=row, column=column, sticky="ew",
               padx=15, pady=4, ipady=7)
    return entry

create_label(form, "Description", 1, 0)
description_entry = create_entry(form, 2, 0)

create_label(form, "Amount (₹)", 1, 1)
amount_entry = create_entry(form, 2, 1)

create_label(form, "Transaction Type", 1, 2)
type_box = ttk.Combobox(
    form, values=["Income", "Expense"],
    state="readonly", font=("Arial", 10)
)
type_box.grid(row=2, column=2, sticky="ew", padx=15, pady=4, ipady=4)
type_box.set("Expense")

categories = [
    "Salary", "Business", "Food", "Travel", "Shopping",
    "Bills", "Rent", "Health", "Education", "Investment", "Other"
]
create_label(form, "Category", 1, 3)
category_box = ttk.Combobox(
    form, values=categories, font=("Arial", 10)
)
category_box.grid(row=2, column=3, sticky="ew", padx=15, pady=4, ipady=4)
category_box.set("Food")

create_label(form, "Date (YYYY-MM-DD)", 3, 0)
date_entry = create_entry(form, 4, 0)
date_entry.insert(0, date.today().isoformat())

for column in range(4):
    form.grid_columnconfigure(column, weight=1)

# SEARCH AND FILTER BAR
filter_bar = tk.Frame(content, bg=BG)
filter_bar.pack(fill="x", pady=7)

tk.Label(
    filter_bar, text="SEARCH", bg=BG, fg=CYAN,
    font=("Arial", 9, "bold")
).pack(side="left", padx=(0, 5))

search_entry = tk.Entry(
    filter_bar, bg=CARD, fg=WHITE,
    insertbackground=WHITE, relief="flat", width=22
)
search_entry.pack(side="left", padx=5, ipady=6)

tk.Label(
    filter_bar, text="TYPE", bg=BG, fg=CYAN,
    font=("Arial", 9, "bold")
).pack(side="left", padx=(10, 4))

type_filter = ttk.Combobox(
    filter_bar, values=["All", "Income", "Expense"],
    state="readonly", width=11
)
type_filter.pack(side="left", padx=4)
type_filter.set("All")

tk.Label(
    filter_bar, text="CATEGORY", bg=BG, fg=CYAN,
    font=("Arial", 9, "bold")
).pack(side="left", padx=(10, 4))

category_filter = ttk.Combobox(
    filter_bar, values=["All"] + categories,
    state="readonly", width=13
)
category_filter.pack(side="left", padx=4)
category_filter.set("All")

# TRANSACTION HISTORY TABLE
tk.Label(
    content, text="TRANSACTION HISTORY",
    font=("Arial", 13, "bold"), fg=CYAN, bg=BG
).pack(anchor="w", pady=(5, 5))

table_frame = tk.Frame(content, bg=PANEL)
table_frame.pack(fill="both", expand=True)

columns = ("ID", "Description", "Amount", "Type", "Category", "Date")
table = ttk.Treeview(
    table_frame, columns=columns, show="headings", height=7
)

column_widths = {
    "ID": 55, "Description": 230, "Amount": 130,
    "Type": 110, "Category": 140, "Date": 150
}
for column in columns:
    table.heading(column, text=column)
    table.column(column, width=column_widths[column], anchor="center")

scrollbar = ttk.Scrollbar(
    table_frame, orient="vertical", command=table.yview
)
table.configure(yscrollcommand=scrollbar.set)
table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# BUTTON HELPER
def create_button(parent, text, color, command):
    return tk.Button(
        parent, text=text, font=("Arial", 9, "bold"),
        bg=color, fg=BG, activebackground=WHITE,
        activeforeground=BG, relief="flat", cursor="hand2",
        padx=12, pady=9, command=command
    )

# FORM HELPERS
def clear_form():
    global editing_id
    editing_id = None
    description_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    type_box.set("Expense")
    category_box.set("Food")
    date_entry.delete(0, tk.END)
    date_entry.insert(0, date.today().isoformat())
    form_title.config(text="ADD NEW TRANSACTION")
    add_button.config(state="normal")
    update_button.config(state="disabled")

def read_form():
    description = description_entry.get().strip()
    amount_text = amount_entry.get().strip()
    transaction_type = type_box.get().strip()
    category = category_box.get().strip()
    transaction_date = date_entry.get().strip()

    if not description or not amount_text or not category:
        messagebox.showwarning("Missing Details", "Please fill all fields.")
        return None

    if transaction_type not in ("Income", "Expense"):
        messagebox.showwarning("Invalid Type", "Choose Income or Expense.")
        return None

    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
        datetime.strptime(transaction_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Enter a positive amount and date in YYYY-MM-DD format."
        )
        return None

    return (
        description, amount, transaction_type,
        category, transaction_date
    )

# DISPLAY AND DASHBOARD
def show_transactions():
    table.delete(*table.get_children())
    cursor.execute("""
        SELECT id, description, amount, type, category, transaction_date
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
    """)

    search_text = search_entry.get().strip().lower()
    selected_type = type_filter.get()
    selected_category = category_filter.get()

    for row in cursor.fetchall():
        if search_text and search_text not in row[1].lower():
            continue
        if selected_type != "All" and row[3] != selected_type:
            continue
        if selected_category != "All" and row[4] != selected_category:
            continue

        table.insert(
            "", "end",
            values=(
                row[0], row[1], f"₹{row[2]:,.2f}",
                row[3], row[4], row[5]
            )
        )

def refresh_dashboard():
    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN type='Income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END), 0)
        FROM transactions
    """)
    total_income, total_expenses = cursor.fetchone()
    balance = total_income - total_expenses

    income_label.config(text=f"₹{total_income:,.2f}")
    expense_label.config(text=f"₹{total_expenses:,.2f}")
    balance_label.config(text=f"₹{balance:,.2f}")
    show_transactions()

search_entry.bind("<KeyRelease>", lambda event: show_transactions())
type_filter.bind("<<ComboboxSelected>>", lambda event: show_transactions())
category_filter.bind("<<ComboboxSelected>>", lambda event: show_transactions())

# ADD TRANSACTION
def add_transaction():
    data = read_form()
    if data is None:
        return

    cursor.execute("""
        INSERT INTO transactions
        (description, amount, type, category, transaction_date)
        VALUES (?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    refresh_dashboard()
    clear_form()
    messagebox.showinfo("Saved", "Transaction added successfully.")

# SELECT AND EDIT TRANSACTION
def edit_transaction():
    global editing_id
    selected = table.selection()
    if not selected:
        messagebox.showwarning("Select Row", "Select a transaction first.")
        return

    values = table.item(selected[0], "values")
    editing_id = int(values[0])

    description_entry.delete(0, tk.END)
    description_entry.insert(0, values[1])

    amount_entry.delete(0, tk.END)
    amount_entry.insert(0, str(values[2]).replace("₹", "").replace(",", ""))

    type_box.set(values[3])
    category_box.set(values[4])

    date_entry.delete(0, tk.END)
    date_entry.insert(0, values[5])

    form_title.config(text=f"EDIT TRANSACTION - ID {editing_id}")
    add_button.config(state="disabled")
    update_button.config(state="normal")

# SAVE EDITED TRANSACTION
def update_transaction():
    if editing_id is None:
        messagebox.showwarning("Edit First", "Select a row and click EDIT SELECTED.")
        return

    data = read_form()
    if data is None:
        return

    cursor.execute("""
        UPDATE transactions
        SET description=?, amount=?, type=?, category=?, transaction_date=?
        WHERE id=?
    """, (*data, editing_id))
    conn.commit()
    refresh_dashboard()
    clear_form()
    messagebox.showinfo("Updated", "Transaction updated successfully.")

# DELETE TRANSACTION
def delete_transaction():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("Select Row", "Select a transaction first.")
        return

    if messagebox.askyesno(
        "Confirm Delete", "Delete the selected transaction?"
    ):
        transaction_id = int(table.item(selected[0], "values")[0])
        cursor.execute(
            "DELETE FROM transactions WHERE id=?",
            (transaction_id,)
        )
        conn.commit()
        refresh_dashboard()
        clear_form()
        messagebox.showinfo("Deleted", "Transaction deleted successfully.")

# MONTHLY REPORT WITH SIMPLE BAR CHART
def monthly_report():
    report_window = tk.Toplevel(root)
    report_window.title("Monthly Financial Report")
    report_window.geometry("650x500")
    report_window.configure(bg=BG)

    tk.Label(
        report_window, text="MONTHLY FINANCIAL REPORT",
        font=("Arial", 18, "bold"), fg=CYAN, bg=BG
    ).pack(pady=15)

    month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
    top = tk.Frame(report_window, bg=BG)
    top.pack(pady=5)

    tk.Label(
        top, text="Month (YYYY-MM):",
        bg=BG, fg=WHITE
    ).pack(side="left", padx=5)

    tk.Entry(
        top, textvariable=month_var, bg=CARD, fg=WHITE,
        insertbackground=WHITE, width=12
    ).pack(side="left", padx=5, ipady=5)

    summary = tk.Label(
        report_window, text="", font=("Arial", 12),
        fg=WHITE, bg=PANEL, justify="left", padx=20, pady=15
    )
    summary.pack(fill="x", padx=20, pady=15)

    chart = tk.Canvas(
        report_window, width=570, height=220,
        bg=PANEL, highlightthickness=0
    )
    chart.pack(padx=20, pady=10)

    def generate_report():
        month_text = month_var.get().strip()
        try:
            datetime.strptime(month_text, "%Y-%m")
        except ValueError:
            messagebox.showerror(
                "Invalid Month", "Enter month as YYYY-MM, e.g. 2026-11."
            )
            return

        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type='Income' THEN amount ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END), 0)
            FROM transactions
            WHERE substr(transaction_date, 1, 7)=?
        """, (month_text,))
        income, expenses = cursor.fetchone()

        summary.config(
            text=(
                f"Month: {month_text}\n\n"
                f"Total Income: ₹{income:,.2f}\n"
                f"Total Expenses: ₹{expenses:,.2f}\n"
                f"Net Balance: ₹{income - expenses:,.2f}"
            )
        )

        chart.delete("all")
        maximum = max(income, expenses, 1)
        baseline = 175
        chart.create_line(45, baseline, 535, baseline, fill=MUTED, width=2)

        for x, amount, color, label in (
            (145, income, GREEN, "INCOME"),
            (345, expenses, RED, "EXPENSES")
        ):
            bar_height = amount / maximum * 125
            chart.create_rectangle(
                x, baseline - bar_height, x + 100, baseline,
                fill=color, outline=""
            )
            chart.create_text(
                x + 50, baseline - bar_height - 15,
                text=f"₹{amount:,.0f}", fill=WHITE,
                font=("Arial", 10, "bold")
            )
            chart.create_text(
                x + 50, 195, text=label, fill=CYAN,
                font=("Arial", 10, "bold")
            )

    tk.Button(
        top, text="GENERATE", bg=CYAN, fg=BG,
        relief="flat", command=generate_report
    ).pack(side="left", padx=8)

    generate_report()

# EXPORT CSV FOR EXCEL
def export_csv():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        initialfile="HimaVamsi_Transactions.csv"
    )
    if not file_path:
        return

    cursor.execute("""
        SELECT id, description, amount, type, category, transaction_date
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
    """)
    rows = cursor.fetchall()

    try:
        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow([
                "ID", "Description", "Amount",
                "Type", "Category", "Date"
            ])
            writer.writerows(rows)
        messagebox.showinfo("Export Complete", "CSV file exported successfully.")
    except OSError as error:
        messagebox.showerror("Export Error", str(error))

# EXPORT PDF USING HTML PRINT-TO-PDF
# Open the report in your browser, press Ctrl+P, and choose
# "Microsoft Print to PDF" or "Save as PDF".
def export_pdf_report():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML Report", "*.html")],
        initialfile="HimaVamsi_Financial_Report.html"
    )
    if not file_path:
        return

    cursor.execute("""
        SELECT id, description, amount, type, category, transaction_date
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
    """)
    rows = cursor.fetchall()

    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN type='Income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='Expense' THEN amount ELSE 0 END), 0)
        FROM transactions
    """)
    income, expenses = cursor.fetchone()
    balance = income - expenses

    table_rows = ""
    for row in rows:
        table_rows += (
            "<tr>"
            f"<td>{row[0]}</td>"
            f"<td>{html.escape(str(row[1]))}</td>"
            f"<td>Rs. {row[2]:,.2f}</td>"
            f"<td>{html.escape(str(row[3]))}</td>"
            f"<td>{html.escape(str(row[4]))}</td>"
            f"<td>{html.escape(str(row[5]))}</td>"
            "</tr>"
        )

    report_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Hima Vamsi Financial Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #172033; }}
h1 {{ color: #087e91; margin-bottom: 4px; }}
.sub {{ color: #667085; margin-top: 0; }}
.cards {{ display: flex; gap: 12px; margin: 24px 0; }}
.card {{ border: 1px solid #cbd5e1; padding: 14px; flex: 1; border-radius: 8px; }}
.card b {{ display: block; margin-bottom: 8px; color: #475569; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
th, td {{ border: 1px solid #cbd5e1; padding: 9px; text-align: left; }}
th {{ background: #eaf5f7; }}
@media print {{ button {{ display: none; }} body {{ margin: 12mm; }} }}
</style>
</head>
<body>
<h1>HIMA VAMSI</h1>
<p class="sub">PERSONAL FINANCE MANAGEMENT - TRANSACTION REPORT</p>
<div class="cards">
<div class="card"><b>TOTAL INCOME</b>Rs. {income:,.2f}</div>
<div class="card"><b>TOTAL EXPENSES</b>Rs. {expenses:,.2f}</div>
<div class="card"><b>TOTAL BALANCE</b>Rs. {balance:,.2f}</div>
</div>
<h2>Transaction History</h2>
<table>
<thead><tr><th>ID</th><th>Description</th><th>Amount</th>
<th>Type</th><th>Category</th><th>Date</th></tr></thead>
<tbody>{table_rows}</tbody>
</table>
<p style="margin-top:28px;color:#667085">
Generated by Hima Vamsi Expense Tracker.
</p>
<button onclick="window.print()">Print / Save as PDF</button>
</body>
</html>"""

    try:
        Path(file_path).write_text(report_html, encoding="utf-8")
        webbrowser.open(Path(file_path).resolve().as_uri())
        messagebox.showinfo(
            "Report Ready",
            "Report opened in your browser.\n"
            "Press Ctrl+P and choose Microsoft Print to PDF or Save as PDF."
        )
    except OSError as error:
        messagebox.showerror("Report Error", str(error))

# BUTTONS
buttons = tk.Frame(content, bg=BG)
buttons.pack(fill="x", pady=8)

add_button = create_button(
    buttons, "+ ADD TRANSACTION", CYAN, add_transaction
)
add_button.pack(side="left", padx=3)

edit_button = create_button(
    buttons, "EDIT SELECTED", YELLOW, edit_transaction
)
edit_button.pack(side="left", padx=3)

update_button = create_button(
    buttons, "UPDATE TRANSACTION", GREEN, update_transaction
)
update_button.pack(side="left", padx=3)
update_button.config(state="disabled")

delete_button = create_button(
    buttons, "DELETE SELECTED", RED, delete_transaction
)
delete_button.pack(side="left", padx=3)

clear_button = create_button(
    buttons, "CLEAR FORM", MUTED, clear_form
)
clear_button.pack(side="left", padx=3)

report_button = create_button(
    buttons, "MONTHLY REPORT", CYAN, monthly_report
)
report_button.pack(side="left", padx=3)

csv_button = create_button(
    buttons, "EXPORT CSV", YELLOW, export_csv
)
csv_button.pack(side="left", padx=3)

pdf_button = create_button(
    buttons, "PDF REPORT", GREEN, export_pdf_report
)
pdf_button.pack(side="left", padx=3)

# FOOTER
tk.Label(
    root,
    text="Hima Vamsi Expense Tracker | Python Desktop Edition V2.0",
    font=("Arial", 9), bg=BG, fg=MUTED
).pack(pady=7)

# START APPLICATION
refresh_dashboard()
clear_form()

def close_app():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
