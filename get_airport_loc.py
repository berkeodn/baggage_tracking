import requests
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
load_dotenv()

    
# This script fetches airport data from the AviationStack API and inserts it into a PostgreSQL database. The script is designed to handle 
# pagination and bulk insertions to efficiently store the data. You can run this script periodically to keep the airport data up to date in 
# your database.   

# Database Configuration
DB_CONFIG = {
        "dbname":os.getenv('PG_DATABASE'),
        "user":os.getenv('PG_USER'),
        "password":os.getenv('PG_PASSWORD'),
        "host":os.getenv('PG_HOST'),
        "port":os.getenv('PG_PORT')
    }

# AviationStack API Configuration
API_KEY = os.getenv('AVIATIONSTACK_API_KEY')
BASE_URL = "http://api.aviationstack.com/v1/airports"
LIMIT = 100  # Max limit allowed per request
OFFSET = 0   # Start from the beginning

# PostgreSQL Table Creation Query
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS public.airport_locations (
    iata_code TEXT PRIMARY KEY,
    airport_name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);
"""

def connect_to_postgres():
    """Establish a connection to PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def create_table():
    """Create the airport_locations table if it doesn't exist."""
    conn = connect_to_postgres()
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_QUERY)
    conn.commit()
    cur.close()
    conn.close()

def fetch_airports_data():
    """Fetch all airport data using pagination."""
    all_airports = []
    offset = 0

    while True:
        url = f"{BASE_URL}?access_key={API_KEY}&limit={LIMIT}&offset={offset}"
        response = requests.get(url)
        data = response.json()

        if "data" not in data or not data["data"]:
            break  # No more data to fetch

        for airport in data["data"]:
            if airport.get("latitude") and airport.get("longitude"):  # Ensure valid coordinates
                all_airports.append({
                    "airport_name": airport.get("airport_name"),
                    "iata_code": airport.get("iata_code"),
                    "latitude": airport.get("latitude"),
                    "longitude": airport.get("longitude")
                })

        offset += LIMIT  # Move to next batch

    return all_airports

def insert_airports_to_db(airports):
    """Insert airport data into PostgreSQL."""
    conn = connect_to_postgres()
    cur = conn.cursor()

    insert_query = sql.SQL("""
        INSERT INTO airport_locations (iata_code, airport_name, latitude, longitude)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (iata_code) DO NOTHING;
    """)

    for airport in airports:
        cur.execute(insert_query, (airport["iata_code"], airport["airport_name"], airport["latitude"], airport["longitude"]))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_table()  # Ensure the table exists
    airports_data = fetch_airports_data()  # Fetch all airport data
    insert_airports_to_db(airports_data)  # Insert data into PostgreSQL
    print(f"Inserted {len(airports_data)} airports into the database.")
