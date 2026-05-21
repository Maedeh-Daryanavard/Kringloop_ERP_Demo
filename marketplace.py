from pricing import average_price


def get_manual_market_average(price_text):
    """
    Example input:
    20, 25, 30, 35
    """
    if not price_text:
        return 0

    prices = []

    for item in price_text.split(","):
        try:
            prices.append(float(item.strip()))
        except ValueError:
            pass

    return average_price(prices)