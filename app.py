import streamlit as st
import pandas as pd
import joblib

from recommender import (
    get_recommendations
)

from promotion import (
    generate_offer
)

df = pd.read_csv(
    "data/OnlineRetail.csv",
    encoding="ISO-8859-1"
)

customer_df = pd.read_csv(
    "models/customer_segments.csv"
)

user_ids = sorted(
    customer_df["CustomerID"]
    .unique()
)

st.title(
    "AI Personalization Platform"
)

selected_user = st.selectbox(
    "Select Customer",
    user_ids
)

history = df[
    df["CustomerID"]
    == selected_user
]

st.subheader(
    "Purchase History"
)

st.dataframe(
    history[
        [
            "Description",
            "Quantity"
        ]
    ].head(20)
)

segment = customer_df[
    customer_df["CustomerID"]
    == selected_user
]["Cluster"].iloc[0]

segment_names = {
    0:"Premium Customer",
    1:"Regular Customer",
    2:"New Customer",
    3:"Discount Shopper"
}

st.success(
    f"Segment : "
    f"{segment_names[segment]}"
)

top5 = get_recommendations(
    selected_user
)

st.subheader(
    "Top 5 Recommendations"
)

clicked = None

for product in top5:

    if st.button(product):

        clicked = product

st.write(top5)

st.subheader(
    "Explainability"
)

st.write(
    "✔ Similar customers bought this"
)

st.write(
    "✔ Frequently purchased product"
)

st.write(
    "✔ Matches shopping behavior"
)

offer = generate_offer(
    segment,
    top5
)

st.subheader(
    "AI Promotion"
)

st.info(
    offer
)

if clicked:

    st.subheader(
        "Realtime Update"
    )

    updated = [
        p for p in top5
        if p != clicked
    ]

    st.write(
        "User clicked:",
        clicked
    )

    st.write(
        "Updated Recommendations:"
    )

    st.write(updated)