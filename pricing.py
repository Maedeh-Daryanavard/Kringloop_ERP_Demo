# def calculate_final_price(base_price, damage_percent):
#     discount = damage_percent / 100
#     final_price = base_price * (1 - discount)
#     return round(final_price, 2)
def calculate_final_price(base_price, damage_percent):
    final_price = base_price * (1 - damage_percent / 100)
    return round(final_price, 2)


def average_price(prices):
    prices = [p for p in prices if p > 0]

    if not prices:
        return 0

    return round(sum(prices) / len(prices), 2)