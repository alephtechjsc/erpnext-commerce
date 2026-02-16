from frappe import _


def get_data():
    return [
        {
            "module_name": "Commerce",
            "type": "module",
            "label": _("Commerce"),
            "color": "#4CAF50",
            "icon": "octicon octicon-briefcase",
            "description": "Sales, Purchase, Inventory and Accounting for trading companies.",
        }
    ]
