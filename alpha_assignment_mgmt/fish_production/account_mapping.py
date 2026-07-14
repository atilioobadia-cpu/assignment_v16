import frappe

"""
Account Auto-Mapping Rules for Fish Production
User never selects accounts or cost centers — system determines from Item + Location + Transaction
"""

# Item → Expense Account mapping
ITEM_ACCOUNT_MAP = {
    "FEED-START": "Feed Consumed - Kasamiko - TBBCL",
    "FEED-GROW": "Feed Consumed - Kasamiko - TBBCL",
    "FEED-FIN": "Feed Consumed - Kasamiko - TBBCL",
    "MED-FISH": "Medicine Consumed - Kasamiko - TBBCL",
    "FNG-STD": "Biological Assets - Nursery Fish - TBBCL",
    "TFISH-KSM": "Sales Revenue - Fish Sales - TBBCL",
}

# Item → Credit Account for stock consumption
ITEM_CREDIT_MAP = {
    "FEED-START": "Inventory - Purchased Fish Feed - TBBCL",
    "FEED-GROW": "Inventory - Purchased Fish Feed - TBBCL",
    "FEED-FIN": "Inventory - Purchased Fish Feed - TBBCL",
    "MED-FISH": "Medicine Inventory - TBBCL",
    "FNG-STD": "Biological Assets - Nursery Fish - TBBCL",
}

# Location → Cost Center mapping
LOCATION_COST_CENTER_MAP = {
    "Broodstock": "Broodstock - Kasamiko - TBBCL",
    "Nursery": "Nursery - Kasamiko - TBBCL",
    "Cage": "Cage Grow-Out - Kasamiko - TBBCL",
    "Feed Store": "Feed Store - Kasamiko - TBBCL",
    "Harvested": "Processing Plant - TBBCL",
    "Damaged": "Farm Overhead - Kasamiko - TBBCL",
}

# Mortality account (when fish die)
MORTALITY_ACCOUNT = "Inventory - Damaged / Obsolete Stock - TBBCL"

# WIP account for production costs
WIP_ACCOUNT = "Work-in-Progress - Fish Production - TBBCL"

# Accrued accounts
ACCRUED_LABOUR = "Accrued Staff Costs - TBBCL"
DEPRECIATION_ACCOUNT = "Depreciation Allocated - Kasamiko - TBBCL"
ACCUM_DEPRECIATION = "Accumulated Depreciation - Cages - Kasamiko - TBBCL"

# Bank and receivable
BANK_ACCOUNT = "CRDB Bank - TZS Operating Account - TBBCL"
DEBTORS_ACCOUNT = "Debtors - TBBCL"
PAYABLES_ACCOUNT = "Accounts Payable - TBBCL"


def get_cost_center_for_location(location_name):
    """Auto-determine cost center from location name"""
    if not location_name:
        return "Farm Overhead - Kasamiko - TBBCL"

    location_name_lower = location_name.lower()
    for keyword, cost_center in LOCATION_COST_CENTER_MAP.items():
        if keyword.lower() in location_name_lower:
            return cost_center

    # Check custom field on Location
    cc = frappe.db.get_value("Location", location_name, "custom_cost_center")
    if cc:
        return cc

    return "Farm Overhead - Kasamiko - TBBCL"


def get_account_for_item(item_code, transaction_type="consumption"):
    """Auto-determine account from item code"""
    if transaction_type == "consumption":
        return ITEM_ACCOUNT_MAP.get(item_code, "Feed Consumed - Kasamiko - TBBCL")
    elif transaction_type == "credit":
        return ITEM_CREDIT_MAP.get(item_code, "Inventory - Purchased Fish Feed - TBBCL")
    elif transaction_type == "mortality":
        return MORTALITY_ACCOUNT
    elif transaction_type == "sales":
        return "Sales Revenue - Fish Sales - TBBCL"
    elif transaction_type == "wip":
        return WIP_ACCOUNT
    return ITEM_ACCOUNT_MAP.get(item_code, "")


def get_batch_valuation(item_code, qty, total_cost):
    """Calculate valuation rate for a batch"""
    if qty and qty > 0:
        return total_cost / qty
    return 0


def auto_set_stock_entry_accounts(stock_entry_doc):
    """Auto-set accounts and cost centers on Stock Entry items"""
    for item in stock_entry_doc.items:
        if not item.cost_center and item.s_warehouse:
            # Determine cost center from source warehouse
            wh_location = frappe.db.get_value("Warehouse", item.s_warehouse, "location")
            if wh_location:
                item.cost_center = get_cost_center_for_location(wh_location)
            else:
                item.cost_center = "Farm Overhead - Kasamiko - TBBCL"

        if not item.expense_account:
            item.expense_account = get_account_for_item(item.item_code, "consumption")


def auto_set_journal_entry_accounts(journal_entry_doc, cycle_name=None):
    """Auto-set accounts on Journal Entry based on type"""
    for account in journal_entry_doc.accounts:
        if not account.cost_center:
            account.cost_center = "Farm Overhead - Kasamiko - TBBCL"
