# cal.py
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from sqlalchemy import create_engine, Column, Integer, Float, String, update
from sqlalchemy.orm import sessionmaker, declarative_base
import json
import os
import math
import time

# --- 1. Database Configuration ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "converter_db")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASS = os.environ.get("DB_PASS", "password")

print("Starting Compute Service (Consumer)...")
print(f"Connecting to Database at {DB_HOST}...")

# Keep retrying until DB is ready
engine = None
while engine is None:
    try:
        # Connection string format: "mysql+mysqlconnector://user:password@host/database"
        db_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
        engine = create_engine(db_url)
        # Try to connect
        with engine.connect() as conn:
            print("Database connected!")
            break # Exit loop on success
    except Exception as e:
        print(f"Database not ready: {e}. Retrying in 5 seconds...")
        time.sleep(5)

# --- 2. Define the Database Model (must match app.py) ---
Base = declarative_base()
class Conversion(Base):
    __tablename__ = 'conversion'
    id = Column(Integer, primary_key=True)
    input_value = Column(Float)
    unit_from = Column(String(80))
    unit_to = Column(String(80))
    status = Column(String(80), default='PENDING')
    result = Column(Float, nullable=True)

# Create a session to talk to the DB
Session = sessionmaker(bind=engine)

# --- 3. Conversion Logic (Same as before) ---
LENGTH_FACTORS = {
    'millimeter': 0.001, 'centimeter': 0.01, 'meter': 1.0, 
    'kilometer': 1000.0, 'inch': 0.0254, 'foot': 0.3048, 
    'yard': 0.9144, 'mile': 1609.34
}
WEIGHT_FACTORS = {
    'milligram': 1e-6, 'gram': 0.001, 'kilogram': 1.0, 
    'ounce': 0.0283495, 'pound': 0.453592
}

def convert_unit(value, unit_from, unit_to, factors):
    if unit_from not in factors or unit_to not in factors: return None
    base_value = value * factors[unit_from]
    converted_value = base_value / factors[unit_to]
    return round(converted_value, 6)

def convert_temperature(value, unit_from, unit_to):
    if unit_from == 'Fahrenheit': celsius = (value - 32) * (5/9)
    elif unit_from == 'Kelvin': celsius = value - 273.15
    else: celsius = value
    if unit_to == 'Fahrenheit': result = (celsius * (9/5)) + 32
    elif unit_to == 'Kelvin': result = celsius + 273.15
    else: result = celsius
    return round(result, 6)

# --- 4. Initialize Kafka Consumer (with Retry Loop) ---
KAFKA_SERVER = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
CONVERSION_TOPIC = 'conversions'

print(f"Connecting to Kafka at {KAFKA_SERVER}...")
consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer(
            CONVERSION_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            auto_offset_reset='earliest',
            group_id='conversion-workers',
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        print("Kafka Consumer connected! Waiting for messages...")
    except NoBrokersAvailable:
        print(f"Kafka not ready. Retrying in 5 seconds...")
        time.sleep(5)
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Retrying in 5 seconds...")
        time.sleep(5)

# --- 5. Run the Consumer Loop ---
for message in consumer:
    session = Session()
    try:
        data = message.value
        task_id = data.get('task_id')
        
        if task_id is None:
            print(f"[COMPUTE_SERVICE] Error: Message has no task_id. {data}")
            continue

        form_id = data.get('form_id')
        value = float(data.get('input_value'))
        unit_from = data.get('unit_from')
        unit_to = data.get('unit_to')
        
        result = None
        if form_id == 'length_form':
            result = convert_unit(value, unit_from, unit_to, LENGTH_FACTORS)
        elif form_id == 'weight_form':
            result = convert_unit(value, unit_from, unit_to, WEIGHT_FACTORS)
        elif form_id == 'temp_form':
            result = convert_temperature(value, unit_from, unit_to)
        
        # --- Update the database ---
        if result is not None:
            session.query(Conversion).filter(Conversion.id == task_id).update({
                'status': 'COMPLETED',
                'result': result
            })
            session.commit()
            print(f"[COMPDOCKERIZE UTE_SERVICE] Processed Task {task_id}: {value} {unit_from} -> {result} {unit_to}")
        else:
            session.query(Conversion).filter(Conversion.id == task_id).update({
                'status': 'FAILED'
            })
            session.commit()
            print(f"[COMPUTE_SERVICE] Failed Task {task_id}: Invalid units {data}")

    except Exception as e:
        session.rollback()
        print(f"[COMPUTE_SERVICE] Error processing message {message.value}: {e}")
    finally:
        session.close()