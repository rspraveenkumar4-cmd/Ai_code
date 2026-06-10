def generate_offer(
        segment,
        products):

    if segment == 0:
        return (
            f"Exclusive 20% OFF on "
            f"{products[0]}"
        )

    elif segment == 1:
        return (
            f"Get 10% OFF on "
            f"{products[0]}"
        )

    elif segment == 2:
        return (
            f"Welcome Coupon ₹500 "
            f"for your next purchase"
        )

    else:
        return (
            f"Buy 1 Get 1 Free on "
            f"{products[0]}"
        )