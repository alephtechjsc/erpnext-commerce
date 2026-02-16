# Deploy ERPNext Commerce on Server

Deploy ERPNext + erpnext_commerce on a fresh Ubuntu server using Docker.

---

## Prerequisites

- Ubuntu server with Docker and Docker Compose installed
- Git installed
- SSH access as root

---

## Step 1: Set Up ERPNext

```bash
cd ~/workspace
git clone https://github.com/frappe/frappe_docker.git erpnext
cd erpnext
cp example.env .env
```

If port 8080 is in use, change it to a free port:

```bash
sed -i 's/"8080:8080"/"8082:8080"/' pwd.yml
```

Start containers:

```bash
docker compose -f pwd.yml up -d
```

---

## Step 2: Wait for ERPNext to Be Ready

> **IMPORTANT:** First run takes 3-5 minutes. Wait for it to finish.

```bash
docker compose -f pwd.yml logs create-site -f
```

Wait until `create-site` exits, then press `Ctrl+C`. Verify:

```bash
docker compose -f pwd.yml exec backend bench --site all list-apps
```

You should see `frappe` and `erpnext`.

---

## Step 3: Install ERPNext Commerce

Clone the install script into the container and run it:

```bash
docker compose -f pwd.yml exec backend bash -c \
  "git clone https://github.com/alephtechjsc/erpnext-commerce.git /tmp/erpnext-commerce && bash /tmp/erpnext-commerce/install.sh frontend && rm -rf /tmp/erpnext-commerce"
```

Restart:

```bash
docker compose -f pwd.yml restart
```

---

## Step 4: Open in Browser

```
http://YOUR_SERVER_IP:8082
```

Login: `Administrator` / `admin`

Check the **Commerce** workspace in the sidebar.

---

## Upgrade

```bash
cd ~/workspace/erpnext
docker compose -f pwd.yml exec backend bash -c "cd /home/frappe/frappe-bench/apps/erpnext-commerce && git pull"
docker compose -f pwd.yml exec backend bench --site frontend migrate
docker compose -f pwd.yml restart
```

---

## Full Reset

```bash
cd ~/workspace/erpnext
docker compose -f pwd.yml down -v
docker compose -f pwd.yml up -d
```

Wait for Step 2, then redo Step 3.

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
| Port already in use | `sed -i 's/"8080:8080"/"FREE_PORT:8080"/' pwd.yml` |
| `DoesNotExistError` on list-apps | Site still creating. Wait for `create-site` to finish. |
| Internal server error | `docker compose -f pwd.yml restart` |
| Workspace not visible | `docker compose -f pwd.yml exec backend bench --site frontend clear-cache` |
| SSH disconnects during migrate | Normal. Migration completes in background. Reconnect and verify. |

---

## What ERPNext Commerce Does

- Activates Commerce domain
- Disables Manufacturing, Projects, HR, Payroll, Education, Agriculture, Non Profit, Healthcare, Hospitality, Quality Management
- Creates 5 roles and 5 role profiles for Sales, Purchase, Stock, Accounts
- Creates Commerce workspace with Sales, Purchase, Inventory, Accounting sections
- Sets naming series: SO-.YYYY.-, PO-.YYYY.-, SINV-.YYYY.-, etc.
- Sets stock valuation to FIFO
- Hides manufacturing fields on Item
