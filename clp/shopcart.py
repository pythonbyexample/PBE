#!/usr/bin/env python3

from collections import defaultdict

prompt      = "> "
cart        = defaultdict(int)
product_tpl = "%d) %-15s [ $%d ]"
products    = {
            1: ("Yoda", 10),
            2: ("DVD", 20),
            3: ("Lego Set", 200)
            }

def product_menu():
    while True:
        print("Select item to order, 'f' when finished.")
        for pid, prod in products.items():
            print(product_tpl % (pid, prod[0], prod[1]))

        inp = input(prompt)
        if inp == 'f': return
        product = getproduct(inp)

        if product : cart[product] += 1
        else       : print("Invalid Input")
        print()

def getproduct(inp):
    try:
        return products[int(inp)]
    except (ValueError, KeyError):
        return None

def main():
    product_menu()

    for (name, price), count in cart.items():
        print("product: %s, price: %d, count: %d" % (name, price, count))
    total = sum(price*count for (name, price), count in cart.items())
    print("Total for the order is: $%d" % total)

main()
