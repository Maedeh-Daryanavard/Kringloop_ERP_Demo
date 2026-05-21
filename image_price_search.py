def average_found_prices(items):
    prices = []

    for item in items:
        price = item.get("price", 0)

        if isinstance(price, (int, float)) and price > 0:
            prices.append(price)

    if not prices:
        return 0

    return round(sum(prices) / len(prices), 2)


def parse_manual_prices(price_text):
    """
    Example:
    20, 25, 30
    """
    if not price_text:
        return 0

    prices = []

    for value in price_text.split(","):
        try:
            price = float(value.strip().replace(",", "."))
            prices.append(price)
        except ValueError:
            pass

    if not prices:
        return 0

    return round(sum(prices) / len(prices), 2)