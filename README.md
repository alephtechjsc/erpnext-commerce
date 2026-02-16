# ERPNext Commerce

A Frappe app that customizes ERPNext for commercial and trading companies. It enables Sales, Purchase, Inventory, and Accounting modules while hiding Manufacturing, Projects, HR, and other irrelevant modules — all without modifying ERPNext core.

## Features

- **Commerce Domain** — activates only the modules relevant to trading companies
- **Custom Roles** — Commerce Admin, Sales User, Purchase User, Stock User, Accounts User
- **Role Profiles** — pre-configured profiles for quick user setup
- **Commerce Workspace** — unified dashboard with Sales, Purchase, Inventory, and Accounting sections
- **Naming Series** — clean, consistent document numbering (SO-2026-00001, SINV-2026-00001, etc.)
- **Hidden Manufacturing Fields** — manufacturing-related fields on Item are hidden by default
- **Disabled Modules** — Manufacturing, Projects, HR, Payroll, Education, Agriculture, Non Profit, Healthcare, Hospitality, Quality Management

## Requirements

- Frappe >= 14.0
- ERPNext >= 14.0
- Python >= 3.10

## Installation

### On an existing bench

```bash
bench get-app https://github.com/alephtechjsc/erpnext-commerce.git
bench --site your-site.local install-app erpnext_commerce
```

### From a local directory

```bash
bench get-app /path/to/erpnext-commerce
bench --site your-site.local install-app erpnext_commerce
```

### After installation

Run a migration to sync fixtures:

```bash
bench --site your-site.local migrate
```

## Upgrade

```bash
bench update --apps erpnext_commerce
bench --site your-site.local migrate
```

## Roles and Profiles

| Role Profile | Roles Included |
|---|---|
| Commerce Admin Profile | Commerce Admin, Sales User, Purchase User, Stock User, Accounts User |
| Sales Profile | Sales User, Stock User |
| Purchase Profile | Purchase User, Stock User |
| Stock Profile | Stock User |
| Accounts Profile | Accounts User |

## Naming Series

| DocType | Default Series |
|---|---|
| Sales Order | SO-.YYYY.- |
| Purchase Order | PO-.YYYY.- |
| Sales Invoice | SINV-.YYYY.- |
| Purchase Invoice | PINV-.YYYY.- |
| Delivery Note | DN-.YYYY.- |
| Purchase Receipt | PR-.YYYY.- |
| Payment Entry | PE-.YYYY.- |
| Journal Entry | JV-.YYYY.- |
| Quotation | QTN-.YYYY.- |
| Material Request | MR-.YYYY.- |
| Stock Entry | STE-.YYYY.- |

## Development

```bash
# Export fixtures after making changes in the UI
bench --site your-site.local export-fixtures --app erpnext_commerce
```

## License

MIT
