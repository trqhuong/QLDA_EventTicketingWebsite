def cart_stats(cart):
    total, total_ticket = 0,0
    if cart:
        for c in cart.values():
            total += c['quantity']*c['price']
            total_ticket += c['quantity']
        return {
            'total' : total,
            'total_ticket' : total_ticket
        }
    else:
        return {
            'total': 0,
            'total_ticket': 0
        }

