#!/usr/bin/env python3
from datetime import datetime, timedelta
from collections import defaultdict
import math, heapq, sys, statistics, re, calendar

# Demo data covering 3 months (Sep, Oct, Nov 2025)
_demo_txns = [
    # ===== Sep 2025 income
    {"id": 1, "date": "2025-09-01", "category": "Salary", "description": "Monthly salary", "amount": 140000.0, "type": "Income"},
    {"id": 2, "date": "2025-09-10", "category": "Freelance", "description": "Gig work", "amount": 12000.0, "type": "Income"},
    # Sep expenses
    {"id": 3, "date": "2025-09-03", "category": "Groceries", "description": "Supermarket", "amount": 6000.0, "type": "Expense"},
    {"id": 4, "date": "2025-09-05", "category": "Food", "description": "Dinner out", "amount": 1500.0, "type": "Expense"},
    {"id": 5, "date": "2025-09-08", "category": "Bills", "description": "Electricity bill", "amount": 5800.0, "type": "Expense"},
    {"id": 6, "date": "2025-09-12", "category": "Transport", "description": "Fuel", "amount": 2200.0, "type": "Expense"},
    {"id": 7, "date": "2025-09-18", "category": "Shopping", "description": "Clothes", "amount": 4500.0, "type": "Expense"},
    {"id": 8, "date": "2025-09-22", "category": "Entertainment", "description": "Movie + snacks", "amount": 900.0, "type": "Expense"},
    # ===== Oct 2025 income
    {"id": 9, "date": "2025-10-01", "category": "Salary", "description": "Monthly salary", "amount": 145000.0, "type": "Income"},
    {"id": 10, "date": "2025-10-14", "category": "Freelance", "description": "Design gig", "amount": 15000.0, "type": "Income"},
    # Oct expenses
    {"id": 11, "date": "2025-10-02", "category": "Groceries", "description": "Supermarket", "amount": 6500.0, "type": "Expense"},
    {"id": 12, "date": "2025-10-06", "category": "Food", "description": "Family dinner", "amount": 2100.0, "type": "Expense"},
    {"id": 13, "date": "2025-10-09", "category": "Bills", "description": "Internet bill", "amount": 2100.0, "type": "Expense"},
    {"id": 14, "date": "2025-10-11", "category": "Transport", "description": "Fuel", "amount": 2400.0, "type": "Expense"},
    {"id": 15, "date": "2025-10-20", "category": "Shopping", "description": "Online order", "amount": 5200.0, "type": "Expense"},
    {"id": 16, "date": "2025-10-25", "category": "Health", "description": "Pharmacy", "amount": 700.0, "type": "Expense"},
    # ===== Nov 2025 income
    {"id": 17, "date": "2025-11-01", "category": "Salary", "description": "Monthly salary", "amount": 150000.0, "type": "Income"},
    {"id": 18, "date": "2025-11-15", "category": "Freelance", "description": "Freelance design", "amount": 25000.0, "type": "Income"},
    # Nov expenses
    {"id": 19, "date": "2025-11-02", "category": "Groceries", "description": "Supermarket", "amount": 7000.0, "type": "Expense"},
    {"id": 20, "date": "2025-11-05", "category": "Food", "description": "Restaurant dinner", "amount": 2400.0, "type": "Expense"},
    {"id": 21, "date": "2025-11-07", "category": "Bills", "description": "Electricity bill", "amount": 6200.0, "type": "Expense"},
    {"id": 22, "date": "2025-11-11", "category": "Bills", "description": "Internet bill", "amount": 2200.0, "type": "Expense"},
    {"id": 23, "date": "2025-11-03", "category": "Transport", "description": "Fuel", "amount": 2500.0, "type": "Expense"},
    {"id": 24, "date": "2025-11-20", "category": "Transport", "description": "Ride share", "amount": 900.0, "type": "Expense"},
    {"id": 25, "date": "2025-11-13", "category": "Shopping", "description": "Clothes", "amount": 8600.0, "type": "Expense"},
    {"id": 26, "date": "2025-11-18", "category": "Entertainment", "description": "Movie + snacks", "amount": 1200.0, "type": "Expense"},
    {"id": 27, "date": "2025-11-21", "category": "Shopping", "description": "Online order", "amount": 4300.0, "type": "Expense"},
    {"id": 28, "date": "2025-11-06", "category": "Health", "description": "Medicine", "amount": 800.0, "type": "Expense"},
    {"id": 29, "date": "2025-11-25", "category": "Gift", "description": "Birthday gift", "amount": 2000.0, "type": "Expense"},
    {"id": 30, "date": "2025-11-28", "category": "Other", "description": "Stationery", "amount": 450.0, "type": "Expense"},
]

transactions = list(_demo_txns)
_next_id = max(t["id"] for t in transactions) + 1 if transactions else 1

# Color codes for terminal output
RESET = "\033[0m"
TITLE = "\033[95m"
OK = "\033[92m"
WARN = "\033[93m"
ERR = "\033[91m"
INFO = "\033[94m"

CATEGORY_KEYWORDS = {
    "Groceries": ["grocery", "supermarket", "veg"],
    "Food": ["restaurant", "dinner", "lunch", "snack", "cafe"],
    "Bills": ["bill", "electricity", "internet", "water", "gas"],
    "Transport": ["fuel", "taxi", "uber", "ride", "bus"],
    "Shopping": ["shop", "clothes", "online", "amazon", "order"],
    "Entertainment": ["movie", "netflix", "concert", "game"],
    "Health": ["medicine", "pharmacy", "doctor", "hospital"],
    "Gift": ["gift", "present"],
    "Rent": ["rent", "rental"],
    "Other": ["other", "stationery", "misc"]
}

BILL_KEYWORDS = ["bill", "electricity", "internet", "water", "gas", "rent", "due"]

# ==================== Helper Functions ====================

def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")

def str_date(d):
    return d.strftime("%Y-%m-%d")

def get_next_id():
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid

def available_months():
    return sorted({t['date'][:7] for t in transactions})

def normalize_category(cat):
    return cat.strip().title() if cat.strip() else "Other"

def auto_categorize(desc, amt=0.0):
    text = (desc or "").lower()
    for cat, keys in CATEGORY_KEYWORDS.items():
        for k in keys:
            if k in text:
                return cat
    if amt >= 20000:
        return "Shopping"
    return "Other"

# ==================== Analysis Functions ====================

def spending_prediction(category, days_back=30, predict_days=7):
    """Predict spending for next N days for a category using trend or monthly averages"""
    last_date = max(parse_date(t['date']) for t in transactions)
    daily = {}
    
    for i in range(days_back):
        d = last_date - timedelta(days=(days_back - 1 - i))
        daily[str_date(d)] = 0.0
    
    for t in transactions:
        if t['type'] == "Expense" and t['category'].lower() == category.lower():
            if t['date'] in daily:
                daily[t['date']] += t['amount']
    
    ys = list(daily.values())
    
    # Use linear trend if data has some variation
    if sum(ys) > 0 and len([y for y in ys if y > 0]) >= 3:
        xs = list(range(len(ys)))
        n = len(xs)
        xm = sum(xs) / n
        ym = sum(ys) / n
        
        num = sum((xs[i] - xm) * (ys[i] - ym) for i in range(n))
        den = sum((xs[i] - xm) ** 2 for i in range(n)) or 1e-6
        
        slope = num / den
        intercept = ym - slope * xm
        
        preds = [max(0.0, intercept + slope * (n - 1 + j)) for j in range(1, predict_days + 1)]
        return {
            "category": category,
            "predicted_total": round(sum(preds), 2),
            "daily": [round(p, 2) for p in preds]
        }
    
    # Fallback: average daily from up to 3 previous months with data
    months = available_months()
    totals = []
    
    for m in reversed(months):
        s = sum(t['amount'] for t in transactions 
                if t['type'] == "Expense" 
                and t['category'].lower() == category.lower() 
                and t['date'].startswith(m))
        
        if s > 0:
            y = int(m[:4])
            mo = int(m[5:7])
            days = calendar.monthrange(y, mo)[1]
            totals.append(s / days)
        
        if len(totals) >= 3:
            break
    
    if not totals:
        return None
    
    avg_daily = sum(totals) / len(totals)
    preds = [round(avg_daily, 2) for _ in range(predict_days)]
    
    return {
        "category": category,
        "predicted_total": round(sum(preds), 2),
        "daily": preds
    }

def detect_spikes(month_year=None, threshold_pct=50.0):
    """Detect spending spikes: compare chosen month to previous month"""
    months = available_months()
    if not months:
        return []
    
    if month_year is None or month_year not in months:
        month_year = months[-1]
    
    idx = months.index(month_year)
    prev_month = months[idx - 1] if idx > 0 else None
    
    def totals_for(m):
        d = defaultdict(float)
        if not m:
            return d
        
        for t in transactions:
            if t['type'] == "Expense" and t['date'].startswith(m):
                d[t['category']] += t['amount']
        return d
    
    cur = totals_for(month_year)
    prev = totals_for(prev_month)
    
    spikes = []
    for c, a in cur.items():
        p = prev.get(c, 0.0)
        
        if p == 0 and a > 0:
            spikes.append({
                "category": c,
                "current": a,
                "previous": 0,
                "note": "New"
            })
        elif p > 0:
            pct = (a - p) / p * 100
            if pct >= threshold_pct:
                spikes.append({
                    "category": c,
                    "current": a,
                    "previous": p,
                    "pct_increase": round(pct, 1)
                })
    
    return spikes

def spending_streak_tracker(month_year=None, daily_budget=None):
    """Track consecutive days below a daily budget"""
    months = available_months()
    if not months:
        return {"streak_days": 0, "daily_budget": 0.0}
    
    if month_year is None or month_year not in months:
        month_year = months[-1]
    
    data = [t for t in transactions if t['date'].startswith(month_year)]
    income = sum(t['amount'] for t in data if t['type'] == "Income")
    expense = sum(t['amount'] for t in data if t['type'] == "Expense")
    
    if daily_budget is None:
        daily_budget = (income * 0.8) / 30 if income > 0 else (expense / 30 if expense > 0 else 0.0)
    
    date_tot = defaultdict(float)
    for t in data:
        if t['type'] == "Expense":
            date_tot[t['date']] += t['amount']
    
    if not date_tot:
        return {"streak_days": 0, "daily_budget": round(daily_budget, 2)}
    
    last_date = max(parse_date(d) for d in date_tot.keys())
    first_date = min(parse_date(d) for d in date_tot.keys())
    
    streak = 0
    cursor = last_date
    
    while True:
        ds = str_date(cursor)
        amt = date_tot.get(ds, 0.0)
        
        if amt <= daily_budget:
            streak += 1
            cursor = cursor - timedelta(days=1)
            
            if cursor < first_date:
                break
        else:
            break
    
    return {"streak_days": streak, "daily_budget": round(daily_budget, 2)}

def financial_health_score(month_year=None):
    """Calculate financial health score (0-100) using simple heuristics"""
    months = available_months()
    if not months:
        return {"score": 0}
    
    if month_year is None or month_year not in months:
        month_year = months[-1]
    
    data = [t for t in transactions if t['date'].startswith(month_year)]
    income = sum(t['amount'] for t in data if t['type'] == "Income")
    expense = sum(t['amount'] for t in data if t['type'] == "Expense")
    
    if income <= 0:
        return {"score": 0}
    
    savings = income - expense
    savings_rate = savings / income
    
    # Base score 0-60 from savings_rate, plus 40 for balanced categories
    s_score = max(0, min(60, savings_rate * 100 * 0.6))
    
    # Category concentration penalty
    cat_tot = defaultdict(float)
    for t in data:
        if t['type'] == "Expense":
            cat_tot[t['category']] += t['amount']
    
    total = sum(cat_tot.values()) or 1.0
    top_share = sum(v for _, v in sorted(cat_tot.items(), key=lambda x: x[1], reverse=True)[:3]) / total if total > 0 else 0
    pareto_score = max(0, 40 - top_share * 40)
    
    final = max(0, min(100, round(s_score + pareto_score, 1)))
    
    return {"score": final, "savings_rate": round(savings_rate * 100, 1)}

def detect_bills_and_next_due(month_year=None):
    """Detect bills and estimate next due date"""
    months = available_months()
    if not months:
        return {}
    
    if month_year is None or month_year not in months:
        month_year = months[-1]
    
    bills = defaultdict(list)
    for t in transactions:
        ds = (t['description'] or "").lower()
        if any(k in ds for k in BILL_KEYWORDS) or t['category'] in ("Bills", "Rent"):
            key = (t['description'].strip().lower() or t['category'])
            bills[key].append((t['date'], t['amount'], t['category']))
    
    reminders = {}
    for key, items in bills.items():
        days = []
        for d, _, _ in items:
            try:
                days.append(parse_date(d).day)
            except:
                pass
        
        if not days:
            continue
        
        avg_day = round(sum(days) / len(days))
        last_date = max(parse_date(d) for d, _, _ in items)
        
        year = last_date.year + (last_date.month // 12)
        month = (last_date.month % 12) + 1
        next_day = min(avg_day, 28)
        
        try:
            next_due = datetime(year, month, next_day)
        except:
            next_due = datetime(year, month, 28)
        
        reminders[key] = {
            "typical_day": avg_day,
            "next_due": str_date(next_due),
            "count": len(items)
        }
    
    return reminders

def pareto_insight(month_year=None):
    """Provide Pareto 80/20 insight"""
    months = available_months()
    if not months:
        return {}
    
    if month_year is None or month_year not in months:
        month_year = months[-1]
    
    data = [t for t in transactions if t['date'].startswith(month_year) and t['type'] == "Expense"]
    cat_tot = defaultdict(float)
    
    for t in data:
        cat_tot[t['category']] += t['amount']
    
    total = sum(cat_tot.values()) or 1.0
    sorted_cats = sorted(cat_tot.items(), key=lambda x: x[1], reverse=True)
    
    running = 0
    cut_off = 0.8 * total
    top = []
    
    for c, a in sorted_cats:
        running += a
        top.append((c, a, round(a / total * 100, 1)))
        
        if running >= cut_off:
            break
    
    return {"total": round(total, 2), "top_cats": top}

# ==================== Transaction Management ====================

def print_tx(t):
    print(f"[{t['id']:3}] {t['date']} | {t['type']:7} | {t['category']:12} | {t['amount']:10.2f} | {t['description']}")

def list_transactions():
    print(TITLE + "\n=== Transactions (recent first) ===" + RESET)
    
    for t in sorted(transactions, key=lambda x: (x['date'], x['id']), reverse=True):
        print_tx(t)
    
    print(INFO + f"\nTotal: {len(transactions)} transactions" + RESET)

def add_transaction():
    print(TITLE + "\nAdd Transaction" + RESET)
    
    t = input("Type (i=Income, e=Expense) -> ").strip().lower()
    if t not in ("i", "e"):
        print(ERR + "Invalid type" + RESET)
        return
    
    typ = "Income" if t == "i" else "Expense"
    
    try:
        amt = float(input("Amount -> ").strip())
    except:
        print(ERR + "Invalid amount" + RESET)
        return
    
    date = input("Date YYYY-MM-DD or Enter for today -> ").strip()
    if not date:
        date = str_date(datetime.now())
    
    desc = input("Description -> ").strip() or "No description"
    
    if typ == "Expense":
        suggested = auto_categorize(desc, amt)
        cat_in = input(f"Category (Enter to accept '{suggested}') -> ").strip()
        cat = suggested if not cat_in else normalize_category(cat_in)
    else:
        cat = input("Category (Salary/Freelance/Other) -> ").strip().title() or "Income"
    
    tx = {
        "id": get_next_id(),
        "date": date,
        "category": cat,
        "description": desc,
        "amount": amt,
        "type": typ
    }
    
    transactions.append(tx)
    print(OK + "Transaction added successfully!" + RESET)
    print_tx(tx)

def edit_transaction():
    try:
        tid = int(input("Enter transaction id -> ").strip())
    except:
        print(ERR + "Invalid id" + RESET)
        return
    
    tx = next((x for x in transactions if x['id'] == tid), None)
    if not tx:
        print(ERR + "Transaction not found" + RESET)
        return
    
    print("\nCurrent transaction:")
    print_tx(tx)
    print()
    
    date = input(f"Date [{tx['date']}] -> ").strip() or tx['date']
    try:
        parse_date(date)
        tx['date'] = date
    except:
        pass
    
    amt = input(f"Amount [{tx['amount']}] -> ").strip() or str(tx['amount'])
    try:
        tx['amount'] = float(amt)
    except:
        pass
    
    tx['description'] = input(f"Description [{tx['description']}] -> ").strip() or tx['description']
    tx['category'] = normalize_category(input(f"Category [{tx['category']}] -> ").strip() or tx['category'])
    
    typ = input(f"Type [{tx['type']}] -> ").strip() or tx['type']
    if typ.capitalize() in ("Income", "Expense"):
        tx['type'] = typ.capitalize()
    
    print(OK + "Transaction updated successfully!" + RESET)
    print_tx(tx)

def delete_transaction():
    try:
        tid = int(input("Enter transaction id to delete -> ").strip())
    except:
        print(ERR + "Invalid id" + RESET)
        return
    
    tx = next((x for x in transactions if x['id'] == tid), None)
    if not tx:
        print(ERR + "Transaction not found" + RESET)
        return
    
    print("\nTransaction to delete:")
    print_tx(tx)
    
    confirm = input("\nAre you sure? (y/n) -> ").strip().lower()
    if confirm == 'y':
        transactions.remove(tx)
        print(OK + "Transaction deleted successfully!" + RESET)
    else:
        print(INFO + "Deletion cancelled" + RESET)

# ==================== Summary Functions ====================

def monthly_summary(month_year=None):
    """Generate monthly summary"""
    months = available_months()
    if not months:
        print(WARN + "No data available" + RESET)
        return
    
    if month_year is None:
        month_year = months[-1]
    
    if month_year not in months:
        print(WARN + "Month not found, using latest" + RESET)
        month_year = months[-1]
    
    data = [t for t in transactions if t['date'].startswith(month_year)]
    income = sum(t['amount'] for t in data if t['type'] == "Income")
    expense = sum(t['amount'] for t in data if t['type'] == "Expense")
    net = income - expense
    
    print(TITLE + f"\n=== Monthly Summary: {month_year} ===" + RESET)
    print(f"Income:    {income:12.2f}")
    print(f"Expense:   {expense:12.2f}")
    print(f"Net:       {net:12.2f}")
    print("-" * 40)
    
    cat_tot = defaultdict(float)
    for t in data:
        if t['type'] == "Expense":
            cat_tot[t['category']] += t['amount']

    
    if cat_tot:
        print("\nExpense Breakdown:")
        for c, a in sorted(cat_tot.items(), key=lambda x: x[1], reverse=True):
            percentage = (a / expense * 100) if expense > 0 else 0
            print(f"  {c:12}: {a:10.2f} ({percentage:5.1f}%)")

def weekly_summary_interactive():
    """Generate weekly summary interactively"""
    try:
        year = int(input("Enter year -> ").strip())
        month = int(input("Enter month (1-12) -> ").strip())
    except:
        print(ERR + "Invalid year/month" + RESET)
        return
    
    choice = input("Enter week number (1..5) or 'last' -> ").strip().lower()
    week_map = defaultdict(list)
    
    for t in transactions:
        d = parse_date(t['date'])
        if d.year == year and d.month == month:
            wk = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
            week_map[wk].append(t)
    
    if not week_map:
        print(WARN + "No data for that month" + RESET)
        return
    
    weeks_sorted = sorted(week_map.keys())
    
    if choice == "last":
        wkkey = weeks_sorted[-1]
    else:
        try:
            idx = int(choice) - 1
            wkkey = weeks_sorted[idx]
        except:
            print(ERR + "Invalid week choice" + RESET)
            return
    
    data = week_map[wkkey]
    income = sum(t['amount'] for t in data if t['type'] == "Income")
    expense = sum(t['amount'] for t in data if t['type'] == "Expense")
    net = income - expense
    
    print(TITLE + f"\n=== Weekly Summary: {wkkey} ===" + RESET)
    print(f"Income:  {income:.2f}")
    print(f"Expense: {expense:.2f}")
    print(f"Net:     {net:.2f}")
    print()
    
    if data:
        print("Transactions:")
        for t in sorted(data, key=lambda x: (x['date'], x['id'])):
            print_tx(t)

def recommendations(month_year=None):
    """Generate financial recommendations"""
    months = available_months()
    if not months:
        print(WARN + "No data available" + RESET)
        return
    
    if month_year is None:
        month_year = months[-1]
    
    data = [t for t in transactions if t['date'].startswith(month_year)]
    income = sum(t['amount'] for t in data if t['type'] == "Income")
    expense = sum(t['amount'] for t in data if t['type'] == "Expense")
    
    print(TITLE + f"\n=== Financial Recommendations for {month_year} ===" + RESET)
    
    if income <= 0:
        print(WARN + "No income data available" + RESET)
        return
    
    savings = income - expense
    pct = savings / income * 100
    
    print(f"Net Savings: {savings:.2f} ({pct:.1f}% of income)")
    print()
    
    if pct < 10:
        print(WARN + "⚠️  Low Savings Rate" + RESET)
        print("- Aim for 15-20% savings rate")
        print("- Review discretionary spending")
        print("- Consider reducing non-essential expenses")
    elif pct < 20:
        print(OK + "✓ Decent Savings Rate" + RESET)
        print("- Good foundation, small optimizations can help")
        print("- Consider automated savings")
        print("- Review recurring expenses")
    else:
        print(OK + "✓ Excellent Savings Rate!" + RESET)
        print("- Keep up the good work!")
        print("- Consider investment opportunities")
    
    print()
    
    cat_tot = defaultdict(float)
    for t in data:
        if t['type'] == "Expense":
            cat_tot[t['category']] += t['amount']
    
    if cat_tot:
        top, amt = sorted(cat_tot.items(), key=lambda x: x[1], reverse=True)[0]
        print(f"Largest Expense Category: {top} (₹{amt:.2f})")
        
        if amt / expense > 0.4:  # If more than 40% of expenses
            print(WARN + f"- {top} accounts for more than 40% of total expenses")
            print("- Consider if this spending aligns with your priorities" + RESET)

# ==================== Menu and UI ====================

def print_welcome():
    print(TITLE + "="*60 + RESET)
    print(TITLE + "           PERSONAL FINANCE TRACKER           " + RESET)
    print(INFO + "  Interactive CLI — Track, Analyze, Optimize  " + RESET)
    print(TITLE + "="*60 + RESET)

def print_menu():
    print("\n" + OK + "="*56 + RESET)
    print(OK + " MAIN MENU ".center(56, "-") + RESET)
    print(" 1) List transactions")
    print(" 2) Add transaction")
    print(" 3) Edit transaction")
    print(" 4) Delete transaction")
    print("-" * 56)
    print(" 5) Monthly summary")
    print(" 6) Weekly summary")
    print("-" * 56)
    print(" 7) Spending Prediction (next 7 days)")
    print(" 8) Expense Spike Detection")
    print(" 9) Spending Streak Tracker")
    print("10) Financial Health Score")
    print("-" * 56)
    print("11) Smart Bill Reminders")
    print("12) Pareto 80/20 Insight")
    print("13) Recommendations")
    print("-" * 56)
    print(" 0) Exit")
    print(OK + "="*56 + RESET)

# ==================== Main Loop ====================

def main():
    print_welcome()
    
    while True:
        print_menu()
        ch = input("\nChoose option -> ").strip()
        
        if ch == "1":
            list_transactions()
        
        elif ch == "2":
            add_transaction()
        
        elif ch == "3":
            edit_transaction()
        
        elif ch == "4":
            delete_transaction()
        
        elif ch == "5":
            mm = input("Enter month (YYYY-MM) or Enter for latest -> ").strip() or None
            monthly_summary(mm)
        
        elif ch == "6":
            weekly_summary_interactive()
        
        elif ch == "7":
            cat = input("Enter category (e.g., Food, Groceries) -> ").strip().title()
            pred = spending_prediction(cat)
            
            if pred:
                print(TITLE + f"\n=== Spending Prediction for {cat} ===" + RESET)
                print(f"Next 7 Days Total: ₹{pred['predicted_total']:.2f}")
                print("\nDaily Predictions:")
                for i, amount in enumerate(pred['daily'], 1):
                    print(f"  Day {i}: ₹{amount:.2f}")
            else:
                print(WARN + "Not enough data to generate prediction." + RESET)
        
        elif ch == "8":
            mm = input("Enter month (YYYY-MM) or Enter for latest -> ").strip() or None
            spikes = detect_spikes(mm if mm else None)
            
            if not spikes:
                print(OK + "No significant spending spikes detected." + RESET)
            else:
                print(WARN + "\n=== Spending Spikes Detected ===" + RESET)
                for s in spikes:
                    if 'note' in s and s['note'] == "New":
                        print(f"● NEW: {s['category']} - ₹{s['current']:.2f} (no previous spending)")
                    else:
                        print(f"● {s['category']}: ₹{s['current']:.2f} vs ₹{s['previous']:.2f} (+{s['pct_increase']:.1f}%)")
        
        elif ch == "9":
            mm = input("Enter month (YYYY-MM) or Enter for latest -> ").strip() or None
            res = spending_streak_tracker(mm if mm else None)
            
            print(INFO + f"\n=== Spending Streak Tracker ===" + RESET)
            print(f"Daily Budget: ₹{res['daily_budget']:.2f}")
            print(f"Streak: {res['streak_days']} consecutive days under budget")
            
            if res['streak_days'] >= 7:
                print(OK + "✓ Great streak! Keep it up!" + RESET)
        
        elif ch == "10":
            mm = input("Enter month (YYYY-MM) or Enter for latest -> ").strip() or None
            score = financial_health_score(mm if mm else None)
            
            print(TITLE + "\n=== Financial Health Score ===" + RESET)
            print(f"Score: {score['score']}/100")
            
            if score['score'] >= 80:
                print(OK + "✓ Excellent financial health!" + RESET)
            elif score['score'] >= 60:
                print(OK + "✓ Good financial health" + RESET)
            elif score['score'] >= 40:
                print(WARN + "⚠️  Moderate financial health - Room for improvement" + RESET)
            else:
                print(ERR + "⚠️  Needs attention - Review spending habits" + RESET)
            
            if 'savings_rate' in score:
                print(f"Savings Rate: {score['savings_rate']:.1f}%")
        
        elif ch == "11":
            mm = input("Enter month (YYYY-MM) or Enter for latest -> ").strip() or None
            rem = detect_bills_and_next_due(mm if mm else None)
            
            if not rem:
                print(OK + "No recurring bills detected." + RESET)
            else:
                print(TITLE + "\n=== Bill Reminders ===" + RESET)
                for k, v in rem.items():
                    print(f"● {k[:30]:30}: Next due {v['next_due']} (seen {v['count']} times)")
        
        elif ch == "12":
            mm = input("Enter month (YYYY-MM) or Enter for latest -> ").strip() or None
            p = pareto_insight(mm if mm else None)
            
            if not p or not p.get("top_cats"):
                print(WARN + "Not enough data for Pareto analysis" + RESET)
            else:
                print(TITLE + f"\n=== Pareto 80/20 Insight for {mm if mm else 'latest'} ===" + RESET)
                print(f"Total Expenses: ₹{p['total']:.2f}")
                print("\nTop categories (80% of expenses):")
                for c, a, pct in p['top_cats']:
                    print(f"  {c:12}: ₹{a:10.2f} ({pct:5.1f}%)")
        
        elif ch == "13":
            mm = input("Enter month (YYYY-MM) or Enter for latest -> ").strip() or None
            recommendations(mm if mm else None)

        elif ch == "0":
            print(INFO + "Goodbye!" + RESET)
            sys.exit(0)
        else:
            print(ERR + "Invalid option" + RESET)
if __name__ == "__main__":
    main()
