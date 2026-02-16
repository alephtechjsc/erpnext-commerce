# Local Testing Guide — ERPNext Commerce

Complete guide to set up a fresh Frappe bench on Ubuntu, install ERPNext + erpnext_commerce, and verify everything works.

---

## Part A: Server Setup (Fresh Ubuntu)

### A1. Install System Dependencies

```bash
sudo apt-get update && sudo apt-get upgrade -y

sudo apt-get install -y \
  python3-dev python3-pip python3-venv python3-setuptools \
  git mariadb-server mariadb-client \
  redis-server nodejs npm \
  libffi-dev libssl-dev libjpeg-dev libxml2-dev libxslt1-dev \
  zlib1g-dev wkhtmltopdf curl supervisor nginx

sudo npm install -g yarn
```

### A2. Secure MariaDB

```bash
sudo mysql_secure_installation
```

- Set a root password (remember it, you'll need it later)
- Answer `Y` to all prompts

### A3. Configure MariaDB for Frappe

```bash
sudo tee -a /etc/mysql/mariadb.conf.d/50-server.cnf > /dev/null << 'EOF'

[mysqld]
innodb-file-format=barracuda
innodb-file-per-table=1
innodb-large-prefix=1
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
EOF

sudo systemctl restart mariadb
```

### A4. Create a Bench User

> Do NOT run bench as root. Create a dedicated user.

```bash
sudo useradd -m -s /bin/bash bench_user
sudo passwd bench_user
sudo usermod -aG sudo bench_user
```

Switch to bench_user for all remaining commands:

```bash
su - bench_user
```

### A5. Install Frappe Bench CLI

```bash
pip3 install frappe-bench
```

Verify:

```bash
bench --version
```

### A6. Initialize Frappe Bench

```bash
cd ~
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
```

### A7. Install ERPNext

```bash
bench get-app --branch version-15 erpnext
```

### A8. Create a Site

Replace `YOUR_MYSQL_ROOT_PASSWORD` with the password you set in step A2.

```bash
bench new-site erp.localhost --mariadb-root-password YOUR_MYSQL_ROOT_PASSWORD --admin-password admin
bench --site erp.localhost install-app erpnext
bench use erp.localhost
```

### A9. Quick Test — ERPNext is Working

```bash
bench start
```

Open `http://YOUR_SERVER_IP:8000` in browser. Login with:
- User: `Administrator`
- Password: `admin`

Press `Ctrl+C` to stop bench after confirming it works.

---

## Part B: Install ERPNext Commerce

> All commands below run as `bench_user` from `~/frappe-bench` directory.

### B1. Get the App

```bash
cd ~/frappe-bench
bench get-app https://github.com/alephtechjsc/erpnext-commerce.git
```

### B2. Install on Your Site

```bash
bench --site erp.localhost install-app erpnext_commerce
```

### B3. Sync Fixtures

```bash
bench --site erp.localhost migrate
```

**Expected output:** No errors. You should see fixture imports for Role, Role Profile, Workspace, Property Setter, Module Def.

---

## Part C: Verify Installation

### C1. Verify App is Installed

```bash
bench --site erp.localhost list-apps
```

**Expected:** `erpnext_commerce` appears in the list alongside `frappe` and `erpnext`.

---

### C2. Verify Commerce Domain is Active

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
frappe.get_single("Domain Settings").active_domains
```

**Expected:** Should include a row with `domain = "Commerce"`.

```python
frappe.db.exists("Domain", "Commerce")
```

**Expected:** Returns `"Commerce"`.

```python
exit()
```

---

### C3. Verify Modules are Disabled

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
disabled = [
    "Manufacturing", "Projects", "HR", "Payroll", "Education",
    "Agriculture", "Non Profit", "Healthcare", "Hospitality", "Quality Management",
]

for mod in disabled:
    app = frappe.db.get_value("Module Def", mod, "app_name")
    print(f"{mod}: app_name='{app}' {'(disabled)' if not app else '(STILL ACTIVE!)'}")

exit()
```

**Expected:** All 10 modules show `(disabled)`.

---

### C4. Verify Stock Settings

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
ss = frappe.get_single("Stock Settings")
print(f"valuation_method: {ss.valuation_method}")
print(f"stock_uom: {ss.stock_uom}")
print(f"show_barcode_field: {ss.show_barcode_field}")
print(f"auto_indent: {ss.auto_indent}")

exit()
```

**Expected output:**

```
valuation_method: FIFO
stock_uom: Nos
show_barcode_field: 1
auto_indent: 1
```

---

### C5. Verify Roles Were Created

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
roles = ["Commerce Admin", "Sales User", "Purchase User", "Stock User", "Accounts User"]
for role in roles:
    exists = frappe.db.exists("Role", role)
    print(f"{role}: {'EXISTS' if exists else 'MISSING!'}")

exit()
```

**Expected:** All 5 roles show `EXISTS`.

---

### C6. Verify Role Profiles Were Created

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
profiles = {
    "Commerce Admin Profile": ["Commerce Admin", "Sales User", "Purchase User", "Stock User", "Accounts User"],
    "Sales Profile": ["Sales User", "Stock User"],
    "Purchase Profile": ["Purchase User", "Stock User"],
    "Stock Profile": ["Stock User"],
    "Accounts Profile": ["Accounts User"],
}

for profile_name, expected_roles in profiles.items():
    if not frappe.db.exists("Role Profile", profile_name):
        print(f"{profile_name}: MISSING!")
        continue
    doc = frappe.get_doc("Role Profile", profile_name)
    actual_roles = sorted([r.role for r in doc.roles])
    expected_sorted = sorted(expected_roles)
    match = actual_roles == expected_sorted
    print(f"{profile_name}: {'OK' if match else 'MISMATCH!'} -> {actual_roles}")

exit()
```

**Expected:** All 5 profiles show `OK` with correct roles.

---

### C7. Verify Commerce Workspace Exists

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
if frappe.db.exists("Workspace", "Commerce"):
    ws = frappe.get_doc("Workspace", "Commerce")
    print(f"Workspace: {ws.name}")
    print(f"Module: {ws.module}")
    print(f"Public: {ws.public}")
    print(f"Links: {len(ws.links)}")
    print(f"Shortcuts: {len(ws.shortcuts)}")
    print(f"Number Cards: {len(ws.number_cards)}")
    print()
    print("Links:")
    for link in ws.links:
        print(f"  - {link.label} -> {link.link_to} ({link.link_type})")
    print()
    print("Shortcuts:")
    for sc in ws.shortcuts:
        print(f"  - {sc.label} -> {sc.link_to}")
else:
    print("Commerce workspace: MISSING!")

exit()
```

**Expected:**
- 18 links (5 Sales + 5 Purchase + 4 Inventory + 4 Accounting)
- 6 shortcuts (Sales Order, Purchase Order, Sales Invoice, Purchase Invoice, Payment Entry, Item)
- 4 number cards

---

### C8. Verify Naming Series (Property Setters)

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
expected = {
    "Sales Order":      "SO-.YYYY.-",
    "Purchase Order":   "PO-.YYYY.-",
    "Sales Invoice":    "SINV-.YYYY.-",
    "Purchase Invoice": "PINV-.YYYY.-",
    "Delivery Note":    "DN-.YYYY.-",
    "Purchase Receipt": "PR-.YYYY.-",
    "Payment Entry":    "PE-.YYYY.-",
    "Journal Entry":    "JV-.YYYY.-",
    "Quotation":        "QTN-.YYYY.-",
    "Material Request": "MR-.YYYY.-",
    "Stock Entry":      "STE-.YYYY.-",
}

for doctype, series in expected.items():
    default = frappe.db.get_value(
        "Property Setter",
        {"doc_type": doctype, "property": "default", "field_name": "naming_series"},
        "value"
    )
    options = frappe.db.get_value(
        "Property Setter",
        {"doc_type": doctype, "property": "options", "field_name": "naming_series"},
        "value"
    )
    default_ok = default == series
    options_ok = options and series in options
    status = "OK" if (default_ok and options_ok) else "ISSUE"
    print(f"{doctype}: default={default} options_has_series={options_ok} [{status}]")

exit()
```

**Expected:** All 11 doctypes show `[OK]`.

---

### C9. Verify Hidden Manufacturing Fields on Item

```bash
bench --site erp.localhost console
```

Paste this into the console:

```python
hidden_fields = ["manufacturing", "is_sub_contracted_item", "default_bom"]

for field in hidden_fields:
    ps = frappe.db.get_value(
        "Property Setter",
        {"doc_type": "Item", "field_name": field, "property": "hidden"},
        "value"
    )
    print(f"Item.{field} hidden: {ps} {'(OK)' if ps == '1' else '(ISSUE!)'}")

exit()
```

**Expected:** All 3 fields show `(OK)`.

---

## Part D: Verify in Browser (UI Check)

Start the bench:

```bash
cd ~/frappe-bench
bench start
```

Open `http://YOUR_SERVER_IP:8000` in browser. Login with `Administrator` / `admin`.

1. **Check Workspace:** Navigate to the sidebar. You should see a **Commerce** workspace. Click it and confirm the 4 sections: Sales, Purchase, Inventory, Accounting.

2. **Check Shortcuts:** On the Commerce workspace, verify the 6 shortcut cards are visible.

3. **Check Number Cards:** Verify the 4 number cards appear (Open Sales Orders, Open Purchase Orders, Unpaid Sales Invoices, Unpaid Purchase Invoices).

4. **Check Naming Series:** Create a new Sales Order. The naming series dropdown should default to `SO-.YYYY.-`.

5. **Check Hidden Fields:** Open any Item. The Manufacturing section, "Is Sub Contracted Item" checkbox, and "Default BOM" field should be hidden.

6. **Check Disabled Modules:** Go to search bar and type "Manufacturing". It should not appear as a module/workspace. Same for Projects, HR, etc.

---

## Uninstall (if needed)

```bash
cd ~/frappe-bench
bench --site erp.localhost uninstall-app erpnext_commerce
bench remove-app erpnext_commerce
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `bench: command not found` | Run `pip3 install frappe-bench` or check PATH |
| `App not found` on get-app | Check the GitHub repo URL is correct and accessible |
| MariaDB connection error | Verify MariaDB is running: `sudo systemctl status mariadb` |
| Fixtures not loading | Run `bench --site erp.localhost migrate` again |
| Workspace not visible | Clear cache: `bench --site erp.localhost clear-cache` then reload browser |
| Roles not showing up | Check domain is active: Commerce domain must be in Domain Settings |
| Naming series not defaulting | Check Property Setters exist via bench console |
| Permission denied errors | Make sure you are running as `bench_user`, not root |
| Node.js version error | Frappe v15 needs Node.js 18+: `node --version` to check |
