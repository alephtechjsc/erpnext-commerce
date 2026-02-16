import frappe
from frappe import _


def after_install():
    """Run after app installation."""
    _setup_domain()
    _disable_unwanted_modules()
    _set_stock_settings()
    _set_naming_series()
    frappe.db.commit()


def get_domain_data():
    """Return domain configuration for Commerce domain."""
    return {
        "set_value": [
            ["Stock Settings", None, "stock_uom", "Nos"],
            ["Stock Settings", None, "valuation_method", "FIFO"],
            ["Stock Settings", None, "show_barcode_field", 1],
            ["Stock Settings", None, "auto_indent", 1],
        ],
        "default_portal_role": "Customer",
        "restricted_roles": [
            "Manufacturing User",
            "Manufacturing Manager",
            "Projects User",
            "Projects Manager",
            "HR User",
            "HR Manager",
            "Education Manager",
        ],
        "modules": [
            "Selling",
            "Buying",
            "Stock",
            "Accounts",
            "CRM",
            "Assets",
        ],
        "custom_fields": {},
    }


def _setup_domain():
    """Activate Commerce domain."""
    if not frappe.db.exists("Domain", "Commerce"):
        frappe.get_doc({"doctype": "Domain", "domain": "Commerce"}).insert(
            ignore_permissions=True
        )

    active_domains = frappe.get_list("Has Domain", filters={"parent": "Domain Settings"}, pluck="domain")
    if "Commerce" not in active_domains:
        domain_settings = frappe.get_single("Domain Settings")
        domain_settings.append("active_domains", {"domain": "Commerce"})
        domain_settings.save(ignore_permissions=True)


# Modules to disable for a trading/commerce company
MODULES_TO_DISABLE = [
    "Manufacturing",
    "Projects",
    "HR",
    "Payroll",
    "Education",
    "Agriculture",
    "Non Profit",
    "Healthcare",
    "Hospitality",
    "Quality Management",
]


def _disable_unwanted_modules():
    """Disable modules not relevant to trading companies."""
    for module_name in MODULES_TO_DISABLE:
        if frappe.db.exists("Module Def", module_name):
            # Disable the module in Module Def
            frappe.db.set_value("Module Def", module_name, "app_name", "")

    # Also block from showing in sidebar via Module Profile
    # These will be hidden when the user does not have roles for them


def _set_stock_settings():
    """Configure stock settings for trading companies."""
    stock_settings = frappe.get_single("Stock Settings")

    stock_settings.valuation_method = "FIFO"
    stock_settings.stock_uom = "Nos"
    stock_settings.show_barcode_field = 1
    stock_settings.auto_indent = 1

    stock_settings.save(ignore_permissions=True)


# Default naming series for commerce doctypes
NAMING_SERIES = {
    "Sales Order": "SO-.YYYY.-",
    "Purchase Order": "PO-.YYYY.-",
    "Sales Invoice": "SINV-.YYYY.-",
    "Purchase Invoice": "PINV-.YYYY.-",
    "Delivery Note": "DN-.YYYY.-",
    "Purchase Receipt": "PR-.YYYY.-",
    "Payment Entry": "PE-.YYYY.-",
    "Journal Entry": "JV-.YYYY.-",
    "Quotation": "QTN-.YYYY.-",
    "Material Request": "MR-.YYYY.-",
    "Stock Entry": "STE-.YYYY.-",
}


def _set_naming_series():
    """Set default naming series for key doctypes."""
    for doctype, series in NAMING_SERIES.items():
        if frappe.db.exists("DocType", doctype):
            meta = frappe.get_meta(doctype)
            if meta.has_field("naming_series"):
                # Add series to options if not present
                current_options = (
                    frappe.db.get_value(
                        "Property Setter",
                        {
                            "doc_type": doctype,
                            "property": "options",
                            "field_name": "naming_series",
                        },
                        "value",
                    )
                    or ""
                )

                if not current_options:
                    field = meta.get_field("naming_series")
                    current_options = field.options or "" if field else ""

                options_list = [
                    o.strip() for o in current_options.split("\n") if o.strip()
                ]

                if series not in options_list:
                    options_list.insert(0, series)

                new_options = "\n".join(options_list)

                # Create or update Property Setter for naming_series options
                ps_name = frappe.db.get_value(
                    "Property Setter",
                    {
                        "doc_type": doctype,
                        "property": "options",
                        "field_name": "naming_series",
                    },
                )

                if ps_name:
                    frappe.db.set_value("Property Setter", ps_name, "value", new_options)
                else:
                    frappe.get_doc(
                        {
                            "doctype": "Property Setter",
                            "doctype_or_docfield": "DocField",
                            "doc_type": doctype,
                            "field_name": "naming_series",
                            "property": "options",
                            "property_type": "Text",
                            "value": new_options,
                            "module": "Commerce",
                        }
                    ).insert(ignore_permissions=True)

                # Set default value
                ps_default = frappe.db.get_value(
                    "Property Setter",
                    {
                        "doc_type": doctype,
                        "property": "default",
                        "field_name": "naming_series",
                    },
                )

                if ps_default:
                    frappe.db.set_value("Property Setter", ps_default, "value", series)
                else:
                    frappe.get_doc(
                        {
                            "doctype": "Property Setter",
                            "doctype_or_docfield": "DocField",
                            "doc_type": doctype,
                            "field_name": "naming_series",
                            "property": "default",
                            "property_type": "Text",
                            "value": series,
                            "module": "Commerce",
                        }
                    ).insert(ignore_permissions=True)
