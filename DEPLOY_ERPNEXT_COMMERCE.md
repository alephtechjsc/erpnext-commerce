# Deploy ERPNext Commerce on Server

Deploy ERPNext + erpnext_commerce on a fresh Ubuntu server using Docker.

---

## Prerequisites

- Ubuntu server (20.04 / 22.04 / 24.04)
- Docker and Docker Compose installed
- Git installed
- SSH access as root

---

## Step 1: Set Up ERPNext with Docker

```bash
cd ~/workspace
git clone https://github.com/frappe/frappe_docker.git erpnext
cd erpnext
cp example.env .env
```

Check if port 8080 is free:

```bash
ss -tlnp | grep 8080
```

If port 8080 is in use, change the port in `pwd.yml` to a free one (e.g. 8082):

```bash
sed -i 's/"8080:8080"/"8082:8080"/' pwd.yml
```

Start the containers:

```bash
docker compose -f pwd.yml up -d
```

Verify all containers are running:

```bash
docker compose -f pwd.yml ps
```

All containers should show `Up` status, including `frontend`.

---

## Step 2: Wait for Site Creation

> **IMPORTANT:** The `pwd.yml` auto-creates a site named `frontend` with ERPNext. This takes 3-5 minutes on first run. **Do NOT run any bench commands until it finishes.**

Watch the progress:

```bash
docker compose -f pwd.yml logs create-site -f
```

Wait until you see output like:

```
create-site-1  | Installing erpnext...
...
create-site-1 exited with code 0
```

Press `Ctrl+C` to stop watching logs.

Then verify:

```bash
docker compose -f pwd.yml exec backend bench --site all list-apps
```

Expected output:

```
frappe  x.x.x
erpnext x.x.x
```

> The default login is `Administrator` / `admin` and the DB password is `123` (from `.env`).

---

## Step 3: Install ERPNext Commerce

Get the app (use `--skip-assets` because the app has no frontend assets):

```bash
docker compose -f pwd.yml exec backend bench get-app --skip-assets https://github.com/alephtechjsc/erpnext-commerce.git
```

Fix the app name in apps.txt (bench registers it with hyphens, but Python needs underscores):

```bash
docker compose -f pwd.yml exec backend sed -i 's/erpnext-commerce/erpnext_commerce/' /home/frappe/frappe-bench/sites/apps.txt
```

Install the app on the site:

```bash
docker compose -f pwd.yml exec backend bench --site frontend install-app erpnext_commerce
```

Run migrate to sync fixtures:

```bash
docker compose -f pwd.yml exec backend bench --site frontend migrate
```

Restart containers:

```bash
docker compose -f pwd.yml restart
```

---

## Step 4: Verify Installation

Open browser: `http://YOUR_SERVER_IP:8082` (or 8080 if you didn't change the port).

Login:
- **User:** `Administrator`
- **Password:** `admin`

### Quick Checks

**Check Commerce workspace** — should appear in the sidebar with Sales, Purchase, Inventory, Accounting sections.

**Check via console:**

```bash
docker compose -f pwd.yml exec backend bench --site frontend console
```

```python
# Verify app is installed
frappe.get_installed_apps()
# Should include 'erpnext_commerce'

# Verify Commerce domain
frappe.db.exists("Domain", "Commerce")
# Should return "Commerce"

# Verify roles
for r in ["Commerce Admin", "Sales User", "Purchase User", "Stock User", "Accounts User"]:
    print(f"{r}: {'OK' if frappe.db.exists('Role', r) else 'MISSING'}")

# Verify naming series
for dt in ["Sales Order", "Purchase Order", "Sales Invoice", "Purchase Invoice"]:
    val = frappe.db.get_value("Property Setter", {"doc_type": dt, "property": "default", "field_name": "naming_series"}, "value")
    print(f"{dt}: {val}")

exit()
```

---

## Upgrade ERPNext Commerce

When there are updates to the app:

```bash
cd ~/workspace/erpnext
docker compose -f pwd.yml exec backend bash -c "cd /home/frappe/frappe-bench/apps/erpnext-commerce && git pull"
docker compose -f pwd.yml exec backend bench --site frontend migrate
docker compose -f pwd.yml restart
```

---

## Full Reset

To completely start over (destroys all data):

```bash
cd ~/workspace/erpnext
docker compose -f pwd.yml down -v
docker compose -f pwd.yml up -d
```

Then wait for `create-site` to finish (Step 2) and re-install erpnext_commerce (Step 3).

---

## Uninstall

```bash
cd ~/workspace/erpnext
docker compose -f pwd.yml exec backend bench --site frontend uninstall-app erpnext_commerce
docker compose -f pwd.yml exec backend bench remove-app erpnext_commerce
docker compose -f pwd.yml restart
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `address already in use` on startup | Change port in `pwd.yml`: `sed -i 's/"8080:8080"/"FREE_PORT:8080"/' pwd.yml` |
| `ModuleNotFoundError: erpnext-commerce` | Fix apps.txt: `docker compose -f pwd.yml exec backend sed -i 's/erpnext-commerce/erpnext_commerce/' /home/frappe/frappe-bench/sites/apps.txt` |
| `DoesNotExistError` on list-apps | Site is still being created. Wait for `create-site` container to finish. |
| Internal server error after install | Restart: `docker compose -f pwd.yml restart` |
| Fixtures not loading | Run: `docker compose -f pwd.yml exec backend bench --site frontend migrate` |
| Workspace not visible | Clear cache: `docker compose -f pwd.yml exec backend bench --site frontend clear-cache` and reload browser |
| Container not starting | Check logs: `docker compose -f pwd.yml logs <service> --tail 50` |
| DB access denied on new-site | Use `--db-root-username root` and the password from `.env` (default: `123`) |
| SSH disconnects during migrate | Normal for long operations. Migration still completes. Reconnect and verify. |

---

## Architecture

```
Docker Containers (pwd.yml)
├── frontend      — Nginx reverse proxy (port 8082 -> 8080)
├── backend       — Frappe/ERPNext application server
├── db            — MariaDB 10.6
├── redis-cache   — Redis for caching
├── redis-queue   — Redis for background jobs
├── websocket     — Real-time updates
├── scheduler     — Background job scheduler
├── queue-short   — Short-running background jobs
├── queue-long    — Long-running background jobs
├── configurator  — Initial config
└── create-site   — Auto-creates site on first run (exits after done)
```

## What ERPNext Commerce Does

- **Activates** Commerce domain
- **Disables** Manufacturing, Projects, HR, Payroll, Education, Agriculture, Non Profit, Healthcare, Hospitality, Quality Management
- **Creates** 5 roles: Commerce Admin, Sales User, Purchase User, Stock User, Accounts User
- **Creates** 5 role profiles: Commerce Admin Profile, Sales Profile, Purchase Profile, Stock Profile, Accounts Profile
- **Creates** Commerce workspace with links to Sales, Purchase, Inventory, Accounting doctypes
- **Sets** naming series: SO-.YYYY.-, PO-.YYYY.-, SINV-.YYYY.-, etc.
- **Sets** stock valuation to FIFO
- **Hides** manufacturing fields on Item doctype
