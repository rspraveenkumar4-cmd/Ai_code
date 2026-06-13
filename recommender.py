import pandas as pd

def get_recommendations(user_id, top_n=5):
    # Re-read CSVs fresh every call so new orders are reflected
    products = pd.read_csv("data/products.csv", dtype=str)
    orders   = pd.read_csv("data/orders.csv",   dtype=str)

    products["Price"]    = pd.to_numeric(products["Price"],    errors="coerce").fillna(0)
    products["Discount"] = pd.to_numeric(products["Discount"], errors="coerce").fillna(0)

    user_id      = str(user_id)
    user_orders  = orders[orders["UserID"] == user_id]
    purchased_ids = set(user_orders["ProductID"].astype(str))

    purchased_products = products[products["ProductID"].astype(str).isin(purchased_ids)]

    # No history → random popular fallback
    if len(purchased_products) == 0:
        return products.sample(min(top_n, len(products)))

    favorite_categories = purchased_products["Category"].value_counts().index.tolist()

    recommendations = products[
        (products["Category"].isin(favorite_categories)) &
        (~products["ProductID"].astype(str).isin(purchased_ids))
    ]

    # Not enough → pad with other unordered products
    if len(recommendations) < top_n:
        extra = products[~products["ProductID"].astype(str).isin(purchased_ids)]
        recommendations = pd.concat([recommendations, extra]).drop_duplicates()

    return recommendations.head(top_n)