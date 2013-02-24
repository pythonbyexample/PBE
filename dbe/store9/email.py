"""Email templates and addresses."""

order_email_tpl = """
Order: #%s
Purchase Order: PO#%s
User: %s
Order Time: %s

ITEMS:
%s

NOTES:
%s

TOTAL: $%s.00
"""

gen9_order_tpl = order_email_tpl + """
Admin Order page: /admin/store9/order/%s/

NOTE: after the order is shipped, mark it 'shipped' on the Admin page.
"""

cust_order_tpl = "Thank you for your order!\n\n" + order_email_tpl
from_address = "orders@gen9.com"
copy_order_to = "ak@ak-desktop.org"
