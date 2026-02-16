# Deploy ERPNext Commerce on Server

Complete guide: from a fresh Ubuntu server to a running ERPNext with Commerce module.

---

## Step 1: Install Docker (skip if already installed)

SSH into your server as root:

```bash
ssh root@YOUR_SERVER_IP
```

Install Docker:

```bash
apt update && apt upgrade -y
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify:

```bash
docker --version
docker compose version
```

---

## Step 2: Install Git (skip if already installed)

```bash
apt install -y git
git --version
```

---

## Step 3: Set Up ERPNext

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/frappe/frappe_docker.git erpnext
cd erpnext
cp example.env .env
```

Check if port 8080 is free:

```bash
ss -tlnp | grep 8080
ps -p 3802442 -o comm,args
kill 3802442
```

If something is using 8080, change to a free port (e.g. 8082):

```bash
sed -i 's/"8080:8080"/"8082:8080"/' pwd.yml
```

Start containers:

```bash
docker compose -f pwd.yml up -d
```

---

## Step 4: Wait for ERPNext to Be Ready

> Make sure you are still in `~/workspace/erpnext` for all remaining steps.

First run creates the database and site. Watch the logs:

```bash
docker compose -f pwd.yml logs create-site -f
```

Wait until you see `create-site` exit (it will stop printing). Then press `Ctrl+C`.

Verify ERPNext is installed:

```bash
docker compose -f pwd.yml exec backend bench --site all list-apps
```

Expected output:

```
frontend
frappe
erpnext
```

If you get `DoesNotExistError`, the site is still being created. Wait and try again.

---

## Step 5: Install ERPNext Commerce

Run this single command:

```bash
docker compose -f pwd.yml exec backend bash -c "git clone https://github.com/alephtechjsc/erpnext-commerce.git /tmp/erpnext-commerce && bash /tmp/erpnext-commerce/install.sh frontend && rm -rf /tmp/erpnext-commerce"
```

You should see steps [1/5] through [5/5] and finally `=== Done! ===`.

Restart:

```bash
docker compose -f pwd.yml restart
```

---

## Step 6: Open in Browser

```
http://YOUR_SERVER_IP:8080
```

(Or `:8082` if you changed the port in Step 3.)

Login: `Administrator` / `admin`

Check the **Commerce** workspace in the sidebar.

---

## Quick Reference (after first setup)

All commands below assume:

```bash
cd ~/workspace/erpnext
```

### Start

```bash
docker compose -f pwd.yml up -d
```

### Stop

```bash
docker compose -f pwd.yml down
```

### Restart

```bash
docker compose -f pwd.yml restart
```

### View Logs

```bash
docker compose -f pwd.yml logs -f backend
```

### Upgrade ERPNext Commerce

```bash
docker compose -f pwd.yml exec backend bash -c "cd /home/frappe/frappe-bench/apps/erpnext-commerce && git pull"
docker compose -f pwd.yml exec backend bench --site frontend migrate
docker compose -f pwd.yml restart
```

### Full Reset (destroys all data)

```bash
docker compose -f pwd.yml down -v
docker compose -f pwd.yml up -d
```

Wait for Step 4, then redo Step 5.

### Uninstall Commerce (keep ERPNext)

```bash
docker compose -f pwd.yml exec backend bench --site frontend uninstall-app erpnext_commerce
docker compose -f pwd.yml exec backend bench remove-app erpnext_commerce
docker compose -f pwd.yml restart
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `docker: command not found` | Redo Step 1 |
| Port already in use | `sed -i 's/"8080:8080"/"FREE_PORT:8080"/' pwd.yml` then restart |
| `DoesNotExistError` on list-apps | Site still creating. Wait for `create-site` to finish |
| Internal server error after install | `docker compose -f pwd.yml restart` |
| Workspace not visible | `docker compose -f pwd.yml exec backend bench --site frontend clear-cache` |
| SSH disconnects during migrate | Normal. Migration completes in background. Reconnect and verify |

---

## What ERPNext Commerce Does

- Activates Commerce domain
- Disables Manufacturing, Projects, HR, Payroll, Education, Agriculture, Non Profit, Healthcare, Hospitality, Quality Management
- Creates 5 roles and 5 role profiles for Sales, Purchase, Stock, Accounts
- Creates Commerce workspace with Sales, Purchase, Inventory, Accounting sections
- Sets naming series: SO-.YYYY.-, PO-.YYYY.-, SINV-.YYYY.-, etc.
- Sets stock valuation to FIFO
- Hides manufacturing fields on Item
