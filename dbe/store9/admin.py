from django.contrib import admin
from models import *


class ProductAdmin(admin.ModelAdmin):
    # Django note: can't display many-to-many field in the list view: 'variation_of',
    list_display = ("short_description", "description", "date_added", "length", "sequence",
                    "contact", "owner", "royalty_rate")
    list_per_page = 100

    list_filter = ("length", "contact", "owner", "royalty_rate")

    list_display_links = ("sequence",)  # name is optional
    search_fields = ("short_description", "description")

    save_on_top = True
admin.site.register(Product, ProductAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_per_page = 100
    save_on_top = True
admin.site.register(AddressBook, AddressAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created", "po_num", "shipped")
    list_filter = ["shipped"]
    search_fields = ["po_num", "user"]
    list_per_page = 100
    save_on_top = True
admin.site.register(Order, OrderAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ("item", "date_added", "quantity")
    list_per_page = 100
    save_on_top = True
admin.site.register(CartItem, CartItemAdmin)

class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "date_added", "active", "sort_order", "sequence")

    # ~3 sec slower because of joins
    # list_display = ["name", "sequence", "_length", "notes", "_contact",
                    # "_owner", "_royalty_rate", "date_added", "sort_order", "active"]
    list_per_page = 100

    list_filter = ["active"]

    list_display_links = ("sequence",)  # name is optional
    search_fields = ["name"]

    save_on_top = True
admin.site.register(Item, ItemAdmin)

class ContactAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "notes", "create_date", "organization_name")
    list_per_page = 100

    list_filter = ("organization_name",)

    list_display_links = ("user",)  # title (pre-name) is optional
    search_fields = ("title", "user", "notes", "organization_name")

    save_on_top = True
admin.site.register(Contact, ContactAdmin)
