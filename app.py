import streamlit as st
import pandas as pd
from collections import Counter
from recommender import get_recommendations
from promotion import generate_offer

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="FreshMart", page_icon="🛒", layout="wide")

# =================================================
# SESSION STATE
# =================================================
if "logged_in"    not in st.session_state: st.session_state.logged_in    = False
if "user_id"      not in st.session_state: st.session_state.user_id      = None
if "cart"         not in st.session_state: st.session_state.cart         = []
if "cart_msg"     not in st.session_state: st.session_state.cart_msg     = ""
if "cart_msg_tab" not in st.session_state: st.session_state.cart_msg_tab = ""
if "order_placed" not in st.session_state: st.session_state.order_placed = False

# =================================================
# BACKGROUND — switches between login and home GIF
# =================================================
LOGIN_GIF = "https://cdn.pixabay.com/animation/2025/02/10/23/22/23-22-39-22_512.gif"
HOME_GIF  = "https://cdn.pixabay.com/animation/2023/07/24/19/40/19-40-09-397_512.gif"
bg_url    = LOGIN_GIF if not st.session_state.logged_in else HOME_GIF

st.markdown(f"""
<style>

/* === ROOT BACKGROUND GIF === */
[data-testid="stApp"] {{
    background-image: url("{bg_url}") !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main > div {{
    background: transparent !important;
}}
[data-testid="stHeader"] {{
    background: rgba(0,0,0,0) !important;
}}

/* === HIDE DEFAULT STREAMLIT PADDING BLOCKS === */
.block-container {{
    padding-top: 2rem;
}}

/* === TYPOGRAPHY === */
h1, h2, h3, h4 {{
    color: #ffffff !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.9);
}}
p, span, label, .stMarkdown {{
    color: #f0f0f0 !important;
}}

/* === SEARCH BOX === */
.stTextInput > div > div > input {{
    background-color: rgba(255,255,255,0.92) !important;
    color: #111 !important;
    border-radius: 10px !important;
    border: 2px solid #00cc66 !important;
}}

/* === LOGIN CONTAINER (uses st.container border) === */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(0,0,0,0.65) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    backdrop-filter: blur(8px) !important;
    padding: 10px !important;
}}

/* === PRODUCT CARD — single self-contained HTML block === */
.fm-card {{
    background: rgba(0,0,0,0.55);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(4px);
    padding: 10px;
    text-align: center;
    margin-bottom: 6px;
}}
.fm-card img {{
    width: 100%;
    height: 160px;
    object-fit: cover;
    border-radius: 10px;
    display: block;
    margin-bottom: 8px;
}}

/* === BUTTONS === */
.stButton > button {{
    background: linear-gradient(135deg, #00cc66, #00aaff) !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600 !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    opacity: 0.85 !important;
}}

/* === TABS === */
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(0,0,0,0.5);
    border-radius: 10px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{ color: #ccc !important; font-weight: 600; }}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, #00cc66, #00aaff) !important;
    border-radius: 8px;
    color: white !important;
}}

</style>
""", unsafe_allow_html=True)

# =================================================
# LOAD DATA
# =================================================
users    = pd.read_csv("data/users.csv",    dtype=str)
products = pd.read_csv("data/products.csv", dtype=str)
orders   = pd.read_csv("data/orders.csv",   dtype=str)

for df, col in [(users,"UserID"),(products,"ProductID"),(orders,"UserID"),(orders,"ProductID")]:
    df[col] = df[col].astype(str)

products["Price"]    = pd.to_numeric(products["Price"],    errors="coerce").fillna(0)
products["Discount"] = pd.to_numeric(products["Discount"], errors="coerce").fillna(0)

# =================================================
# PRODUCT IMAGES
# =================================================
product_images = {
    "Apple":    "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?w=400&h=300&fit=crop",
    "Banana":   "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400&h=300&fit=crop",
    "Orange":   "https://images.unsplash.com/photo-1587735243615-c03f25aaff15?w=400&h=300&fit=crop",
    "Grapes":   "https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=400&h=300&fit=crop",
    "Mango":    "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400&h=300&fit=crop",
    "Tomato":   "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400&h=300&fit=crop",
    "Potato":   "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&h=300&fit=crop",
    "Onion":    "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400&h=300&fit=crop",
    "Carrot":   "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=300&fit=crop",
    "Cucumber": "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400&h=300&fit=crop",
    "Pineapple": "https://imgs.search.brave.com/Yi_5Dyk05tBaK2ogZVIVo7WXpNGNqwBQyioW1gGyr7Y/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMTE2/MzQ4MzE3NC9waG90/by9yaXBlLXBpbmVh/cHBsZS1mcnVpdC1j/dXQtaW4tdHJpYW5n/bGUtc2hhcGUuanBn/P3M9NjEyeDYxMiZ3/PTAmaz0yMCZjPW0x/TnhUTzZWbUxLYUdy/cUNHNDBORko3cDI5/ZmxUU25oNm5GNk1r/bEx6Vjg9",
    "Watermelon":  "https://plus.unsplash.com/premium_photo-1663855531381-f9c100b3c48f?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTN8fHdhdGVybWVsb258ZW58MHx8MHx8fDA%3D",
    "Papaya": "https://plus.unsplash.com/premium_photo-1664391808687-55acdf5c7317?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8cGFwYXlhfGVufDB8fDB8fHww",
    "Pomegranate": "https://plus.unsplash.com/premium_photo-1668076515507-c5bc223c99a4?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8cG9tZWdyYW5hdGV8ZW58MHx8MHx8fDA%3D",
    "Guava": "https://media.istockphoto.com/id/1014779162/photo/pink-guava-for-sale-pune.webp?a=1&b=1&s=612x612&w=0&k=20&c=I_X9jBVVwdS097z8bcXK80rItvXXEPiiULTDfmH3V-Y=",
    "Beans": "https://images.unsplash.com/photo-1560252030-9fc63cb78dac?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTl8fEJlYW5zfGVufDB8fDB8fHww",
    "Cabbage": "https://images.unsplash.com/photo-1591586007768-40725cc562a1?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8Y2FiYmFnZXxlbnwwfHwwfHx8MA%3D%3D",
    "Cauliflower": "https://images.unsplash.com/photo-1692956706779-576c151ec712?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8Y2F1bGlmbG93ZXJ8ZW58MHx8MHx8fDA%3D",
    "Brinjal": "https://images.unsplash.com/photo-1613881553903-4543f5f2cac9?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8QnJpbmphbHxlbnwwfHwwfHx8MA%3D%3D",
    "Ladies Finger": "https://images.unsplash.com/photo-1664289242854-e99d345cfa92?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8bGFkeWZpbmdlcnxlbnwwfHwwfHx8MA%3D%3D"

}
fallback_img = "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&h=300&fit=crop"


# =================================================
# LOGIN PAGE
# =================================================
if not st.session_state.logged_in:

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align:center;font-size:3rem;'>🥬 Welcome to FreshMart</h1>"
        "<p style='text-align:center;font-size:1.1rem;opacity:0.85;'>"
        "Fresh produce, delivered to your door.</p>",
        unsafe_allow_html=True
    )

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        # Use st.container(border=True) — Streamlit native styled box, no stray divs
        with st.container(border=True):
            st.markdown("### 🔐 Sign In")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            if st.button("Login 🚀"):
                user = users[
                    (users["Username"].str.strip() == username.strip()) &
                    (users["Password"].str.strip() == password.strip())
                ]
                if len(user) > 0:
                    st.session_state.logged_in = True
                    st.session_state.user_id   = str(user.iloc[0]["UserID"])
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

    st.stop()

# =================================================
# SIDEBAR — user profile + logout
# =================================================
with st.sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background: rgba(0,0,0,0.75) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        [data-testid="stSidebar"] * { color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    user_row = users[users["UserID"] == str(st.session_state.user_id)].iloc[0]
    uname    = user_row["Username"]
    initials = uname[:2].upper()

    st.markdown(
        f"""
        <div style="text-align:center;padding:20px 0 10px">
            <div style="width:64px;height:64px;border-radius:50%;
                        background:linear-gradient(135deg,#00cc66,#00aaff);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.6rem;font-weight:700;color:white;margin:0 auto 10px">
                {initials}
            </div>
            <div style="font-size:1.1rem;font-weight:700">👋 Hello, {uname}!</div>
            <div style="font-size:0.78rem;opacity:0.6;margin-top:3px">Welcome back</div>
        </div>
        <hr style="border-color:rgba(255,255,255,0.15);margin:0 0 16px"/>
        """,
        unsafe_allow_html=True
    )

    cart_count = len(st.session_state.cart)
    st.markdown(
        f"""
        <div style="background:rgba(255,255,255,0.08);border-radius:10px;
                    padding:10px 14px;margin-bottom:10px;
                    display:flex;justify-content:space-between;align-items:center">
            <span>🛒 Cart Items</span>
            <span style="background:linear-gradient(135deg,#00cc66,#00aaff);
                         border-radius:20px;padding:2px 10px;font-weight:700">
                {cart_count}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🚪 Logout", use_container_width=True):
        for key in ["logged_in","user_id","cart","cart_msg","cart_msg_tab","order_placed"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# =================================================
# USER DATA
# =================================================
user_id     = str(st.session_state.user_id)
user_orders = orders[orders["UserID"] == user_id]
history     = (
    user_orders.merge(products, on="ProductID", how="left")
    if len(user_orders) > 0 else pd.DataFrame()
)
bought_ids  = set(user_orders["ProductID"].tolist())
recommended = get_recommendations(user_id, top_n=5)

# =================================================
# PRODUCT CARD HELPER
# Key fix: image + text are ONE st.markdown() block.
# The Add button is a separate st.button() BELOW — no wrapping divs.
# =================================================
def product_card(row, key_prefix):
    img_url     = product_images.get(row.ProductName, fallback_img)
    disc_pct    = float(row.Discount) if row.Discount else 0.0
    base_price  = float(row.Price)
    final_price = base_price * (1 - disc_pct / 100)

    if disc_pct > 0:
        price_html = (
            f"<span style='text-decoration:line-through;opacity:0.5;color:#ccc'>₹{base_price:.0f}</span> "
            f"<b style='color:#00ee88;font-size:1.1em'>₹{final_price:.0f}</b> "
            f"<span style='background:#ff4444;color:white;font-size:0.7em;"
            f"padding:2px 6px;border-radius:4px;margin-left:4px'>{disc_pct:.0f}% OFF</span>"
        )
    else:
        price_html = f"<b style='font-size:1.1em;color:white'>₹{base_price:.0f}</b>"

    promo      = generate_offer(str(row.Category))
    promo_html = (f"<div style='margin-top:6px;font-size:0.75em;background:rgba(255,200,0,0.18);"
                  f"border:1px solid rgba(255,200,0,0.4);border-radius:6px;padding:3px 6px;"
                  f"color:#ffe066'>{promo}</div>")

    # ONE single markdown block = no black box artifacts
    st.markdown(f"""
    <div class="fm-card">
        <img src="{img_url}" alt="{row.ProductName}"/>
        <div style="font-weight:700;font-size:1em;color:white;margin-bottom:2px">{row.ProductName}</div>
        <div style="font-size:0.8em;color:#aaa;margin-bottom:4px">{row.Category}</div>
        {price_html}
        {promo_html}
    </div>
    """, unsafe_allow_html=True)

    # Button sits naturally below the card HTML — no wrapping div needed
    return st.button("🛒 Add to Cart", key=f"{key_prefix}_{row.ProductID}")

# =================================================
# TABS
# =================================================
tab1, tab2, tab3 = st.tabs(["🏠 Home", "🛒 Cart", "📦 Orders"])

# --- HOME ---
with tab1:
    st.title("🛒 FreshMart")
    st.markdown("*Handpicked freshness, every day.*")

    if st.session_state.cart_msg_tab == "home" and st.session_state.cart_msg:
        st.success(st.session_state.cart_msg)
        st.session_state.cart_msg = ""
        st.session_state.cart_msg_tab = ""

    search = st.text_input("🔍 Search Products", placeholder="e.g. mango, vegetable …")

    def filter_products(df, query):
        if query.strip():
            q = query.lower()
            return df[df["ProductName"].str.lower().str.contains(q) |
                      df["Category"].str.lower().str.contains(q)]
        return df

    filtered  = filter_products(products, search)
    searching = search.strip() != ""

    if not searching and len(recommended) > 0:
        st.subheader("🔥 Recommended For You")
        cols = st.columns(min(5, len(recommended)))
        for i, row in enumerate(recommended.itertuples()):
            with cols[i % len(cols)]:
                if product_card(row, "rec"):
                    st.session_state.cart.append(row.ProductID)
                    st.session_state.cart_msg     = f"✅ **{row.ProductName}** added to cart!"
                    st.session_state.cart_msg_tab = "home"
                    st.rerun()

    st.subheader(f'🔍 Results for "{search}"' if searching else "🛍️ All Products")

    if len(filtered) == 0:
        st.info("No products match your search.")
    else:
        cols = st.columns(4)
        for i, row in enumerate(filtered.itertuples()):
            with cols[i % 4]:
                if product_card(row, "all"):
                    st.session_state.cart.append(row.ProductID)
                    st.session_state.cart_msg     = f"✅ **{row.ProductName}** added to cart!"
                    st.session_state.cart_msg_tab = "home"
                    st.rerun()

# --- CART ---
with tab2:
    st.title("🛒 Your Cart")

    if st.session_state.cart_msg_tab == "cart" and st.session_state.cart_msg:
        st.info(st.session_state.cart_msg)
        st.session_state.cart_msg     = ""
        st.session_state.cart_msg_tab = ""

    if st.session_state.order_placed:
        st.success("🎉 Order placed! Fresh groceries are on the way.")
        st.session_state.order_placed = False

    if len(st.session_state.cart) == 0:
        st.warning("🛒 Your cart is empty. Head to Home and add some items!")
    else:
        qty_map  = Counter(st.session_state.cart)
        cart_df  = products[products["ProductID"].isin(qty_map.keys())].copy()
        total    = 0.0

        st.markdown("---")
        for row in cart_df.itertuples():
            qty        = qty_map[row.ProductID]
            disc_pct   = float(row.Discount) if row.Discount else 0.0
            base_price = float(row.Price)
            unit_price = base_price * (1 - disc_pct / 100)
            line_total = unit_price * qty
            total     += line_total

            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
            with c1: st.markdown(f"**{row.ProductName}**")
            with c2:
                if disc_pct > 0:
                    st.markdown(
                        f"<s style='opacity:0.5'>₹{base_price:.0f}</s> "
                        f"<b style='color:#00ee88'>₹{unit_price:.0f}</b>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f"₹{unit_price:.2f}")
            with c3: st.markdown(f"Qty: **{qty}**")
            with c4: st.markdown(f"**₹{line_total:.2f}**")
            with c5:
                if st.button("❌", key=f"rm_{row.ProductID}"):
                    st.session_state.cart.remove(row.ProductID)
                    st.session_state.cart_msg     = f"🗑️ **{row.ProductName}** removed."
                    st.session_state.cart_msg_tab = "cart"
                    st.rerun()
            st.markdown("---")

        st.success(f"🧾 **Order Total: ₹{total:.2f}**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🛍️ Continue Shopping"):
                st.info("Head back to the Home tab!")
        with col_b:
            if st.button("✅ Place Order"):
                import datetime, os
                # Save each cart item as a new order row in orders.csv
                orders_path = "data/orders.csv"
                if os.path.exists(orders_path):
                    existing = pd.read_csv(orders_path, dtype=str)
                else:
                    existing = pd.DataFrame(columns=["UserID", "ProductID", "OrderDate"])

                # Only add products not already in this user's order history
                already_ordered = set(
                    existing[existing["UserID"] == str(user_id)]["ProductID"].tolist()
                )
                new_pids = set(st.session_state.cart) - already_ordered

                if new_pids:
                    new_rows = [{"UserID": user_id, "ProductID": pid,
                                 "OrderDate": datetime.date.today().isoformat()}
                                for pid in new_pids]
                    updated = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
                    updated.to_csv(orders_path, index=False)
                st.session_state.cart = []
                st.session_state.order_placed = True
                st.rerun()

# --- ORDERS ---
with tab3:
    st.title("📦 Order History")
    if len(history) == 0:
        st.warning("📭 No previous orders found.")
    else:
        st.markdown(f"You have ordered **{len(history)}** item(s) so far.")
        cols = [c for c in ["ProductName","Category","Price","Discount"] if c in history.columns]
        df_show = history[cols].copy()
        df_show.index = range(1, len(df_show)+1)
        st.dataframe(df_show, use_container_width=True)