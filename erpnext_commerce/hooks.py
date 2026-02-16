app_name = "erpnext_commerce"
app_title = "ERPNext Commerce"
app_publisher = "Aleph Tech JSC"
app_description = "ERPNext customization for commercial/trading companies"
app_email = "dev@alephtech.com"
app_license = "MIT"
app_version = "0.1.0"

# Required apps
required_apps = ["frappe", "erpnext"]

# App includes (CSS/JS)
# app_include_css = "/assets/erpnext_commerce/css/erpnext_commerce.css"
# app_include_js = "/assets/erpnext_commerce/js/erpnext_commerce.js"

# After install hook
after_install = "erpnext_commerce.commerce.setup.install.after_install"

# Fixtures - synced on bench migrate
fixtures = [
    {
        "dt": "Module Def",
        "filters": [["module_name", "=", "Commerce"]],
    },
    {
        "dt": "Role",
        "filters": [
            [
                "name",
                "in",
                [
                    "Commerce Admin",
                    "Sales User",
                    "Purchase User",
                    "Stock User",
                    "Accounts User",
                ],
            ]
        ],
    },
    {
        "dt": "Role Profile",
        "filters": [
            [
                "name",
                "in",
                [
                    "Commerce Admin Profile",
                    "Sales Profile",
                    "Purchase Profile",
                    "Stock Profile",
                    "Accounts Profile",
                ],
            ]
        ],
    },
    {
        "dt": "Workspace",
        "filters": [["name", "=", "Commerce"]],
    },
]
# Property Setters are created by install.py (_set_naming_series)
# and exported via: bench --site SITE export-fixtures --app erpnext_commerce

# Domains
domains = {
    "Commerce": "erpnext_commerce.commerce.setup.domain",
}
