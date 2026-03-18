import streamlit as st
import pandas as pd

st.title("Car Sharing Dashboard")
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

st.write("Trips:", trips.head())
st.write("Cars:", cars.head())
st.write("Cities:", cities.head())


# Merge trips + cars
trips_merged = trips.merge(
    cars,
    left_on="car_id",
    right_on="id",
    suffixes=("_trip", "_car")
)

# Merge with cities
trips_merged = trips_merged.merge(
    cities,
    on="city_id",
    how="left"
)

# Optional cleaning
columns_to_drop = ["customer_id"]
existing_cols = [col for col in columns_to_drop if col in trips_merged.columns]
trips_merged = trips_merged.drop(columns=existing_cols)

# Check result
st.write("Merged data:", trips_merged.head())
st.write("Merged columns:", trips_merged.columns)


trips_merged["pickup_time"] = pd.to_datetime(trips_merged["pickup_time"])
trips_merged["dropoff_time"] = pd.to_datetime(trips_merged["dropoff_time"])

trips_merged["pickup_date"] = trips_merged["pickup_time"].dt.date

trips_merged["trip_duration_hours"] = (
    trips_merged["dropoff_time"] - trips_merged["pickup_time"]
).dt.total_seconds() / 3600

cars_brand = st.sidebar.multiselect(
    "Select the Car Brand",
    trips_merged["brand"].dropna().unique()
)

if cars_brand:
    trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

# Compute business performance metrics
total_trips = len(trips_merged)
total_distance = trips_merged["distance"].sum()

# Car model with the highest revenue
top_car = trips_merged.groupby("model")["revenue"].sum().idxmax()

# Display metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Trips", value=total_trips)

with col2:
    st.metric(label="Top Car Model by Revenue", value=top_car)

with col3:
    st.metric(label="Total Distance (km)", value=f"{total_distance:,.2f}")

st.subheader("Preview of merged dataset")
st.write(trips_merged.head())

st.subheader("Trips Over Time")

trips_over_time = trips_merged.groupby("pickup_date").size()
st.line_chart(trips_over_time)

st.subheader("Revenue Per Car Model")

revenue_per_model = trips_merged.groupby("model")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(revenue_per_model)

st.subheader("Revenue by City")

revenue_by_city = trips_merged.groupby("city_name")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(revenue_by_city)