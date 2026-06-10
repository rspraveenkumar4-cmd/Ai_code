import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df = pd.read_csv(
    "data/OnlineRetail.csv",
    encoding="ISO-8859-1"
)

df = df.dropna(subset=["CustomerID"])

df["TotalAmount"] = (
    df["Quantity"] * df["UnitPrice"]
)

customer_df = df.groupby(
    "CustomerID"
).agg({
    "InvoiceNo":"nunique",
    "Quantity":"sum",
    "TotalAmount":"sum"
}).reset_index()

customer_df.columns = [
    "CustomerID",
    "TotalOrders",
    "TotalQuantity",
    "TotalSpent"
]

X = customer_df[
    [
        "TotalOrders",
        "TotalQuantity",
        "TotalSpent"
    ]
]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(
    n_clusters=4,
    random_state=42
)

customer_df["Cluster"] = (
    kmeans.fit_predict(X_scaled)
)

joblib.dump(
    kmeans,
    "models/kmeans.pkl"
)

joblib.dump(
    scaler,
    "models/scaler.pkl"
)

customer_df.to_csv(
    "models/customer_segments.csv",
    index=False
)

print("Training Completed")