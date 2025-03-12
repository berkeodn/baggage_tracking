import json
import psycopg2
from kafka import KafkaConsumer
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Kafka and PostgreSQL settings
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = "baggage_tracking"
PG_HOST = "postgres"
PG_DATABASE = "baggage_tracking"


# Retrieve PostgreSQL credentials from environment variables
PG_USER = os.getenv('PG_USER')  # PostgreSQL user from docker-compose
PG_PASSWORD = os.getenv('PG_PASSWORD')  # PostgreSQL password from docker-compose

# Initialize PostgreSQL connection
def connect_to_postgres():
    conn = psycopg2.connect(
        dbname=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST
    )
    return conn

# Initialize Kafka consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest'
)

# Function to insert event into PostgreSQL database
def insert_event_into_db(events):
    conn = connect_to_postgres()
    cursor = conn.cursor()
    
    # Prepare SQL query
    query = """
    INSERT INTO baggage_tracking (baggage_id, passenger_id, scanner_location, airport_code, date, time, flight_number, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (baggage_id) DO UPDATE
    SET 
        passenger_id = EXCLUDED.passenger_id,
        scanner_location = EXCLUDED.scanner_location,
        airport_code = EXCLUDED.airport_code,
        date = EXCLUDED.date,
        time = EXCLUDED.time,
        flight_number = EXCLUDED.flight_number,
        status = EXCLUDED.status;
    """
    
  # Batch insert
    for event in events:
        cursor.execute(query, (
            event['baggage_id'],
            event['passenger_id'],
            event['scanner_location'],
            event['airport_code'],
            event['date'],
            event['time'],
            event.get('flight_number', 'N/A'),
            event['status']
        ))
    
    # Commit and close connection
    conn.commit()
    cursor.close()
    conn.close()

# Consume messages from Kafka and store in PostgreSQL
def consume_and_store(interval_seconds=30):
    events = []
    last_poll_time = time.time()

    while True:
        # Poll Kafka every X seconds (based on interval_seconds)
        if time.time() - last_poll_time >= interval_seconds:
            messages = consumer.poll(timeout_ms=1000)  # Poll with a timeout
            for topic_partition, messages in messages.items():
                for message in messages:
                    events.append(message.value)
            
            # If we have accumulated enough messages, process them in bulk
            if events:
                print(f"Consumed {len(events)} events, inserting into DB.")
                insert_event_into_db(events)
                events.clear()  # Clear events after processing
            
            last_poll_time = time.time()  # Update the poll time
        
        # Sleep briefly to prevent high CPU usage (optional)
        time.sleep(0.5)

if __name__ == "__main__":
    print("Starting Kafka consumer...")
    consume_and_store()