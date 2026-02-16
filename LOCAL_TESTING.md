# Verify ERPNext Commerce Installation

After deploying with `DEPLOY_ERPNEXT_COMMERCE.md`, use this guide to verify everything works.

All commands run from `~/workspace/erpnext`.

---

## 1. Verify App is Installed

```bash
docker compose -f pwd.yml exec backend bench --site frontend list-apps
```

**Expected:** `frappe`, `erpnext`, `erpnext_commerce`

---

## 2. Verify Commerce Domain is Active

```bash
docker compose -f pwd.yml exec backend bench --site frontend console <<'EOF'
print(frappe.db.exists("Domain", "Commerce"))
ds = frappe.get_single("Domain Settings")
for d in ds.active_domains:
    print(f"  active: {d.domain}")
EOF
```

**Expected:** `Commerce` exists and is listed as active.

---

## 3. Verify Modules are Disabled

```bash
docker compose -f pwd.yml exec backend bench --site frontend console <<'EOF'
disabled = [
    "Manufacturing", "Projects", "HR", "Payroll", "Education",
    "Agriculture", "Non Profit", "Healthcare", "Hospitality", "Quality Management",
]
for mod in disabled:
    app = frappe.db.get_value("Module Def", mod, "app_name")
    print(f"  {mod}: {'disabled' if not app else 'STILL ACTIVE!'}")
EOF
```

**Expected:** All 10 show `disabled`.

---

## 4. Verify Stock Settings

```bash
docker compose -f pwd.yml exec backend bench --site frontend console <<'EOF'
ss = frappe.get_single("Stock Settings")
print(f"  valuation_method: {ss.valuation_method}")
print(f"  show_barcode_field: {ss.show_barcode_field}")
print(f"  auto_indent: {ss.auto_indent}")
EOF
```

**Expected:**

```
valuation_method: FIFO
show_barcode_field: 1
auto_indent: 1
```

---

## 5. Verify Roles

```bash
docker compose -f pwd.yml exec backend bench --site frontend console <<'EOF'
roles = ["Commerce Admin", "Sales User", "Purchase User", "Stock User", "Accounts User"]
for role in roles:
    exists = frappe.db.exists("Role", role)
    print(f"  {role}: {'OK' if exists else 'MISSING!'}")
EOF
```

**Expected:** All 5 show `OK`.

---

## 6. Verify Role Profiles

```bash
docker compose -f pwd.yml exec backend bench --site frontend console <<'EOF'
profiles = {
    "Commerce Admin Profile": ["Commerce Admin", "Sales User", "Purchase User", "Stock User", "Accounts User"],
    "Sales Profile": ["Sales User", "Stock User"],
    "Purchase Profile": ["Purchase User", "Stock User"],
    "Stock Profile": ["Stock User"],
    "Accounts Profile": ["Accounts User"],
}
for name, expected in profiles.items():
    if not frappe.db.exists("Role Profile", name):
        print(f"  {name}: MISSING!")
        continue
    doc = frappe.get_doc("Role Profile", name)
    actual = sorted([r.role for r in doc.roles])
    ok = actual == sorted(expected)
    print(f"  {name}: {'OK' if ok else 'MISMATCH!'} {actual}")
EOF
```

**Expected:** All 5 show `OK`.

---

## 7. Verify Commerce Workspace

```bash
docker compose -f pwd.yml exec backend bench --site frontend console <<'EOF'
if frappe.db.exists("Workspace", "Commerce"):
    ws = frappe.get_doc("Workspace", "Commerce")
    print(f"  Workspace: {ws.name}")
    print(f"  Module: {ws.module}")
    print(f"  Public: {ws.public}")
    print(f"  Links: {len(ws.links)}")
    print(f"  Shortcuts: {len(ws.shortcuts)}")
    print()
    print("  Links:")
    for link in ws.links:
        print(f"    - {link.label} -> {link.link_to}")
    print()
    print("  Shortcuts:")
    for sc in ws.shortcuts:
        print(f"    - {sc.label} -> {sc.link_to}")
else:
    print("  Commerce workspace: MISSING!")
EOF
```

**Expected:** 18 links, 6 shortcuts.

---

## 8. Verify Naming Series

```bash
docker compose -f pwd.yml exec backend bench --site frontend console <<'EOF'
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
    ok = default == series
    print(f"  {doctype}: {default} {'OK' if ok else 'ISSUE!'}")
EOF
```

**Expected:** All 11 show `OK`.

---

## 9. Browser Check

Open `http://YOUR_SERVER_IP:8080` (or `:8082`). Login: `Administrator` / `admin`.

Check:

1. **Commerce workspace** visible in sidebar
2. **4 sections** in workspace: Sales, Purchase, Inventory, Accounting
3. **6 shortcut cards** at top of workspace
4. **Create a Sales Order** — naming series defaults to `SO-.YYYY.-`
5. **Open any Item** — Manufacturing section is hidden
6. **Search "Manufacturing"** — should not appear as a module
