import streamlit as st
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px

# Set page configuration for responsive layout
st.set_page_config(layout="wide")

load_dotenv()

# Create SQLAlchemy Engine
@st.cache_resource
def get_engine():
    return create_engine(
        f"postgresql://{st.secrets['PG_USER']}:{st.secrets['PG_PASSWORD']}@{st.secrets['PG_HOST']}:{st.secrets['PG_PORT']}/{st.secrets['PG_DATABASE']}"
    )

# Query Execution Function
def run_query(query):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Database Query Error: {e}")
        df = pd.DataFrame()
    return df

# Fetch baggage tracking with location
def fetch_baggage_data():
    query = """
        SELECT bt.baggage_id, bt.status, bt.scanner_location, bt.airport_code, 
               bt.flight_number, bt.date, bt.time, al.airport_name, 
               al.latitude, al.longitude 
        FROM baggage_tracking bt
        LEFT JOIN airport_locations al 
        ON bt.airport_code = al.iata_code
        WHERE al.airport_name IS NOT NULL;
    """
    return run_query(query)

# Fetch delayed & lost baggage percentage by airport
def fetch_agg_data():
    query = """
        SELECT 
            airport_code,
            COUNT(*) AS total_baggage,
            SUM(CASE WHEN status IN ('Delayed', 'Lost') THEN 1 ELSE 0 END) AS delayed_lost_baggage,
            (SUM(CASE WHEN status IN ('Delayed', 'Lost') THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS delayed_lost_percentage
        FROM baggage_tracking
        GROUP BY airport_code
        ORDER BY delayed_lost_percentage DESC;

    """
    return run_query(query)

# Fetch Data
df = fetch_baggage_data()
agg_df = fetch_agg_data()

# Dashboard Title
st.title("✈️ Baggage Movement & Delayed/Lost Baggage Monitoring")

# Dropdown Menu for Filtering with 'All' as an option
airport_list = ['All'] + df["airport_code"].unique().tolist()
airport_selected = st.selectbox("Select Airport Code to Filter Data", options=airport_list, index=0)

# Filter data based on selected airport
if airport_selected == 'All':
    df_filtered = df
    agg_df_filtered = agg_df
else:
    df_filtered = df[df["airport_code"] == airport_selected]
    agg_df_filtered = agg_df[agg_df["airport_code"] == airport_selected]

# Use columns for a responsive layout
col1, col2 = st.columns([3, 2])

# 📊 Baggage Status Distribution (Bar Chart) on the left column
with col1:
    st.subheader("📊 Baggage Status Distribution")
    status_counts = df_filtered["status"].value_counts()
    fig_status = px.bar(status_counts, x=status_counts.index, y=status_counts.values, 
                        labels={'x': 'Status', 'y': 'Count'}, title=f"Baggage Status Count for {airport_selected if airport_selected != 'All' else 'All Airports'}")
    st.plotly_chart(fig_status, use_container_width=True)

# 🚨 Delayed & Lost Baggage Percentage by Airport (Bar Chart) on the right column
with col2:
    st.subheader("🚨 Delayed & Lost Baggage Percentage by Airport")
    if not agg_df_filtered.empty:
        fig_airport_percentage = px.bar(agg_df_filtered, x="airport_code", y="delayed_lost_percentage", 
                                        labels={"airport_code": "Airport Code", "delayed_lost_percentage": "Delayed/Lost Baggage Percentage"}, 
                                        title=f"Delayed & Lost Baggage Percentage for {airport_selected if airport_selected != 'All' else 'All Airports'}")
        st.plotly_chart(fig_airport_percentage, use_container_width=True)
    else:
        st.write("No aggregate data available for delayed and lost baggage for this airport.")

# Use columns for a responsive layout
col1, col2 = st.columns([3, 2])

# 📍 Baggage Tracking on Map with Delayed/Lost Baggage Percentage (on the left column)
with col1:
    st.subheader(f"🌍 Baggage Tracking on Map with Delayed/Lost Baggage Percentage for {airport_selected if airport_selected != 'All' else 'All Airports'}")
    if not df_filtered.empty:
        # Merge the baggage data with the aggregated delayed/lost percentage data
        merged_df = df_filtered.groupby('airport_code').agg(
            latitude=('latitude', 'first'),
            longitude=('longitude', 'first'),
            airport_name=('airport_name', 'first'),
            total_baggage=('status', 'count')
        ).reset_index()

        # Calculate delayed and lost baggage percentage for each airport
        merged_df['delayed_lost_percentage'] = merged_df['airport_code'].map(
            agg_df_filtered.set_index('airport_code')['delayed_lost_percentage']
        )

        # Increase the size of the markers and plot the map
        fig_map = px.scatter_geo(
            merged_df, lat="latitude", lon="longitude", hover_name="airport_name",
            hover_data=["airport_name", "airport_code", "delayed_lost_percentage"],
            color="delayed_lost_percentage",width=1200, height=600,  
            projection="natural earth", title=f"Baggage Movement Across {airport_selected if airport_selected != 'All' else 'All Airports'} with Delayed/Lost Baggage Percentage",
            color_continuous_scale="Viridis"
        )
        
        # Update marker size for better visibility
        fig_map.update_traces(marker=dict(size=12))
        
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.write("No location data available for mapping.")

# 🛫 Baggage Distribution by Airport Code (Pie Chart) (on the right column)
with col2:
    st.subheader("✈️ Baggage Distribution by Airport Code")
    airport_counts = df["airport_code"].value_counts()
    fig_airport = px.pie(airport_counts, names=airport_counts.index, values=airport_counts.values, width=1200, height=700,
                         title=f"Baggage Distribution for All Airports")
    st.plotly_chart(fig_airport, use_container_width=True)
