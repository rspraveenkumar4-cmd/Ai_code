import pandas as pd

df = pd.read_csv(
    "data/OnlineRetail.csv",
    encoding="ISO-8859-1"
)

df = df.dropna(
    subset=["CustomerID"]
)

def get_recommendations(
        customer_id,
        top_n=5):

    user_history = df[
        df["CustomerID"] == customer_id
    ]

    purchased = set(
        user_history["Description"]
    )

    recommendations = (
        df.groupby("Description")
        ["Quantity"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    final = []

    for product in recommendations.index:

        if product not in purchased:
            final.append(product)

        if len(final) == top_n:
            break

    return final