#!/bin/bash
# Install erpnext_commerce on a Frappe/ERPNext Docker bench
# Usage: docker compose -f pwd.yml exec backend bash /path/to/install.sh

set -e

SITE=${1:-frontend}
APP_REPO="https://github.com/alephtechjsc/erpnext-commerce.git"
APP_DIR="/home/frappe/frappe-bench/apps/erpnext-commerce"
APPS_TXT="/home/frappe/frappe-bench/sites/apps.txt"

echo "=== Installing erpnext_commerce on site: $SITE ==="

# Step 1: Clone if not already present
if [ ! -d "$APP_DIR" ]; then
    echo "[1/5] Getting app..."
    bench get-app --skip-assets "$APP_REPO"
else
    echo "[1/5] App already cloned, pulling latest..."
    cd "$APP_DIR" && git pull && cd /home/frappe/frappe-bench
fi

# Step 2: Fix apps.txt (bench registers with hyphens, Python needs underscores)
echo "[2/5] Fixing apps.txt..."
sed -i 's/erpnext-commerce/erpnext_commerce/' "$APPS_TXT"

# Step 3: Install on site
echo "[3/5] Installing app on site $SITE..."
bench --site "$SITE" install-app erpnext_commerce

# Step 4: Migrate
echo "[4/5] Running migrate..."
bench --site "$SITE" migrate

# Step 5: Clear cache
echo "[5/5] Clearing cache..."
bench --site "$SITE" clear-cache

echo ""
echo "=== Done! ==="
echo "Restart containers: docker compose -f pwd.yml restart"
echo "Then open your site in browser."
