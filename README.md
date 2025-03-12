
# Baggage Tracking and Monitoring System

This project is a comprehensive **baggage tracking and monitoring system** built using Docker, Kafka, PostgreSQL, Streamlit, and Plotly. The application tracks baggage status, provides insights into delayed or lost baggage, and visualizes the data on interactive dashboards.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Getting Started](#getting-started)
4. [Docker Setup](#docker-setup)
5. [Streamlit Dashboard](#streamlit-dashboard)
6. [Database Schema](#database-schema)
7. [Project Structure](#project-structure)
8. [License](#license)

---

## Project Overview

This project provides a **baggage tracking system** where users can:

- Track baggage status and its current location in airports.
- Visualize data about delayed or lost baggage.
- View statistical insights about baggage handling across airports.

The system integrates with a **PostgreSQL database** for storing baggage data, a **Kafka message queue** for handling real-time events, and a **Streamlit dashboard** for interactive data visualization.

---

## Technology Stack

- **Docker**: Used for containerizing all the services.
- **PostgreSQL**: Database for storing baggage tracking data.
- **Kafka**: Message broker for real-time baggage event processing.
- **Streamlit**: Python framework used for building the interactive dashboard.
- **Plotly**: Visualization library for generating interactive plots.
- **SQLAlchemy**: ORM used to interact with PostgreSQL.

---

## Getting Started

Follow the steps below to get the project up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

- Docker (with Docker Compose)
- Python (for running the Streamlit app)
- PostgreSQL (if not using Docker)

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/baggage-tracking.git
cd baggage-tracking
```

### Step 2: Set Up the Environment Variables

Create a `.env` file in the root directory of your project with the following environment variables:

```bash
PG_USER=your_pg_user
PG_PASSWORD=your_pg_password
PG_HOST=postgres
PG_PORT=5432
PG_DATABASE=baggage_tracking
```

Make sure to replace the placeholders with your actual database credentials.

### Step 3: Build and Start Docker Containers

Ensure Docker and Docker Compose are installed and running. Then, build and start the containers:

```bash
docker-compose up --build
```

This will start all the necessary services (PostgreSQL, Kafka, producer, consumer, pgAdmin, and the Streamlit app).

### Step 4: Access the Application

- **Streamlit Dashboard**: Access the dashboard at `http://localhost:8501`.
- **pgAdmin**: Access the database management UI at `http://localhost:80` (login with the credentials `admin@admin.com` / `admin`).

---

## Docker Setup

The `docker-compose.yml` file defines the following services:

1. **Kafka**: Used for managing the real-time data flow of baggage events.
2. **PostgreSQL**: Database that stores baggage tracking information.
3. **Producer**: Sends real-time baggage data into the Kafka queue.
4. **Consumer**: Processes messages from Kafka and inserts data into PostgreSQL.
5. **pgAdmin**: Web interface for PostgreSQL management.
6. **Streamlit**: Web application that visualizes the data.

To start the application, run:

```bash
docker-compose up
```

### Service Details

- **Kafka**: Exposes port `9092` for Kafka communication.
- **PostgreSQL**: Exposes port `5432` for database connection.
- **pgAdmin**: Exposes port `80` for the web interface.
- **Streamlit**: Exposes port `8501` for the dashboard.

---

## Streamlit Dashboard

The Streamlit dashboard visualizes the baggage tracking data and provides insights into the status of baggage, delayed and lost baggage, and geographic information about the baggage's location.

### Key Features

- **Baggage Status Distribution**: Displays the count of baggage items based on their status (e.g., delayed, lost).
- **Delayed/Lost Baggage Percentage**: Shows the percentage of delayed or lost baggage for each airport.
- **Baggage Tracking Map**: Displays baggage locations on a map, colored by the delayed/lost baggage percentage.
- **Baggage Distribution by Airport**: A pie chart showing baggage distribution across airports.

---

## Database Schema

The PostgreSQL database contains the following tables:

1. **baggage_tracking**: Stores information about baggage items.
   - `baggage_id`: Unique identifier for baggage.
   - `status`: Current status of the baggage (e.g., delayed, lost).
   - `scanner_location`: Location where the baggage was scanned.
   - `airport_code`: Code of the airport.
   - `flight_number`: Flight number associated with the baggage.
   - `date`: Date of tracking.
   - `time`: Time of tracking.
   - `scanner_location`: Physical location of the scanner.

2. **airport_locations**: Stores airport information.
   - `iata_code`: IATA airport code.
   - `airport_name`: Name of the airport.
   - `latitude`: Latitude of the airport.
   - `longitude`: Longitude of the airport.

---

## Project Structure

Here’s a high-level overview of the project structure:

```
baggage-tracking/
│
├── docker-compose.yml         # Docker Compose configuration for services
├── .env                       # Environment variables for the project
├── app/
│   ├── streamlit_dashboard.py  # Streamlit dashboard app
│   ├── requirements.txt       # Python dependencies for Streamlit app
│   ├── kafka_consumer.py      # Kafka consumer for processing messages
│   └── kafka_producer.py      # Kafka producer for sending messages
│
├── data/                      # Sample data (if applicable)
│   └── baggage_tracking.csv   # Sample data for testing
│
└── README.md                  # Project documentation
```
