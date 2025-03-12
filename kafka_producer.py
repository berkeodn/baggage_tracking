import random
import json
import time
from faker import Faker
from datetime import datetime
from kafka import KafkaProducer
import pytz

fake = Faker()

# Define airports with IATA codes and their locations
LOCATIONS = [
    {"name": "IST", "location": "Check-in T1"},
    {"name": "SAW", "location": "Check-in T2"},
    {"name": "BUD", "location": "Check-in T3"},
    {"name": "LAX", "location": "Security Checkpoint"},
    {"name": "DXB", "location": "Loading T1"},
    {"name": "ORD", "location": "Loading T2"},
    {"name": "CDG", "location": "Arrival Gate"},
    {"name": "LHR", "location": "Baggage Claim"},
    {"name": "SIN", "location": "On Carousel"},
    {"name": "HKG", "location": "Customs"},
    {"name": "SYD", "location": "Security Screening"},
    {"name": "JFK", "location": "Baggage Check-in"},
    {"name": "FRA", "location": "Loading T3"},
    {"name": "NRT", "location": "Arrival Hall"},
    {"name": "KUL", "location": "Arrival Gate"},
    {"name": "SEA", "location": "Check-in T4"},
    {"name": "MEX", "location": "Loading T4"}
]

FLIGHT_NUMBERS = [
    "TK193", "TK456", "TK789", "LH123", "LAX100", "DXB202", "ORD303", "PRG404",
    "BA220", "UA205", "AF123", "QF999", "DL150", "KL300", "LH450", "SW123", "AA350", 
    "NZ600", "FI301", "SU522"
]

STATUS = [
    "Checked-in", "Security Cleared", "Loaded on Plane", "In Transit", 
    "Arrived at Destination", "Delayed", "Lost", "Transferred", 
    "Picked Up", "On Carousel"
]

# Kafka settings
KAFKA_BROKER = "kafka:9092"  # Kafka broker address
TOPIC_NAME = "baggage_tracking"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def generate_baggage_event():
    """Generate a new baggage event in the required format with airport codes"""
    location = random.choice(LOCATIONS)  # Select a random location from the list
    return {
        "baggage_id": f"BAG{fake.random_number(digits=5)}",  # Random baggage ID like 'BAG12345'
        "passenger_id": f"PAX{fake.random_number(digits=5)}",  # Random passenger ID like 'PAX67890'
        "scanner_location": location["location"],  # Scanner location (e.g., "Check-in T1")
        "airport_code": location["name"],  # Airport IATA code (e.g., "IST")
        "date": datetime.now(pytz.utc).strftime('%Y-%m-%d'),  # Current date in UTC (YYYY-MM-DD format)
        "time": datetime.now(pytz.utc).strftime('%H:%M:%S'),  # Current time in UTC (HH:MM:SS format)
        "flight_number": random.choice(FLIGHT_NUMBERS),  # Random flight number
        "status": random.choice(STATUS)  # Random event status
    }

def stream_baggage_tracking(interval=10):
    """Simulate real-time baggage tracking data streaming with Kafka"""
    try:
        while True:
            event = generate_baggage_event()
            producer.send(TOPIC_NAME, value=event)
            print(f"Produced: {json.dumps(event, indent=4)}")
        
            time.sleep(interval)  # Simulate delay (e.g., every 2 seconds)
    except KeyboardInterrupt:
        print("Streaming stopped manually.")
    finally:
        producer.close()  # Ensure Kafka producer is properly closed

# Start streaming events to Kafka
stream_baggage_tracking()
