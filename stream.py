import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    cleaned = pd.read_csv(r"C:\Data science\Project4-SwiggyAnalysis\cleaned_data.csv")
    clustered = pd.read_csv(r"C:\Data science\Project4-SwiggyAnalysis\encoded_data_Cluster.csv")

   
    if "city_cleaned" in cleaned.columns and "city" not in cleaned.columns:
        cleaned = cleaned.rename(columns={"city_cleaned": "city"})

   
    cluster_col = "Cluster" if "Cluster" in clustered.columns else "cluster"
    cleaned["cluster"] = clustered[cluster_col].values

    return cleaned

df = load_data()

st.title("🍽️ Restaurant Recommendation App")

st.write(
    "Find Your Favourite Restaurant. "
    "Then we'll recommend other restaurants for you."
)

st.sidebar.header("🔍 Search Filters")



city_options = ["All"] + sorted(df["city"].dropna().unique().tolist())
selected_city = st.sidebar.selectbox("City", city_options)

cuisine_options = ["All"] + sorted(df["cuisine"].dropna().unique().tolist())
selected_cuisine = st.sidebar.selectbox("Cuisine", cuisine_options)

min_rating = float(df["rating"].min())
max_rating = float(df["rating"].max())
selected_min_rating = st.sidebar.slider(
    "Minimum rating",
    min_value=round(min_rating, 1),
    max_value=round(max_rating, 1),
    value=3.5,
    step=0.1,
)

min_cost = int(df["cost"].min())
max_cost = int(df["cost"].max())
selected_cost_range = st.sidebar.slider(
    "Cost range (₹)",
    min_value=min_cost,
    max_value=max_cost,
    value=(min_cost, max_cost),
    step=50,
)



filtered = df.copy()

if selected_city != "All":
    filtered = filtered[filtered["city"] == selected_city]

if selected_cuisine != "All":
    filtered = filtered[filtered["cuisine"] == selected_cuisine]

filtered = filtered[
    (filtered["rating"] >= selected_min_rating)
    & (filtered["cost"] >= selected_cost_range[0])
    & (filtered["cost"] <= selected_cost_range[1])
]



st.subheader("🎯 Top 5 Restaurants")

if filtered.empty:
    st.warning("No restaurants match your filters. Try changing city, cuisine, rating or cost.")
else:
    
    filtered_sorted = filtered.sort_values(
        by=["rating", "rating_count"],
        ascending=[False, False]
    )

    top5 = filtered_sorted.head(5)

    
    st.dataframe(
        top5[["name", "city", "cuisine", "rating", "rating_count", "cost", "cluster"]]
        .reset_index(drop=True)
    )

   

    st.subheader("💸 Cost-based Recommendations (Same Cluster)")

    
    clusters_top5 = top5["cluster"].unique()

   
    remaining = filtered_sorted[~filtered_sorted.index.isin(top5.index)]

    
    remaining_same_cluster = remaining[remaining["cluster"].isin(clusters_top5)]

    if remaining_same_cluster.empty:
        st.info("Not enough restaurants in the same cluster to generate cost-based recommendations.")
    else:
       
        cost_based = remaining_same_cluster.sort_values(
            by=["cost", "rating"],
            ascending=[True, False]
        )

        max_reco = min(30, len(cost_based))
        top_n_cost = st.slider(
            "Number of cost-based recommendations to show",
            min_value=3,
            max_value=max_reco,
            value=min(10, max_reco),
            key="cost_reco_slider",
        )

        st.dataframe(
            cost_based.head(top_n_cost)[
                ["name", "city", "cuisine", "rating", "rating_count", "cost", "cluster"]
            ].reset_index(drop=True)
        )
