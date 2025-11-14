# app.py
from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy  # <-- Import SQLAlchemy
import json
import os
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# --- 1. Initialize App, CORS, and Swagger ---
app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# --- 2. Database Configuration ---
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "converter_db")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASS = os.environ.get("DB_PASS", "password")

# Connection string format: "mysql+mysqlconnector://user:password@host/database"
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 3. Define the Database Model ---
class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input_value = db.Column(db.Float)
    unit_from = db.Column(db.String(80))
    unit_to = db.Column(db.String(80))
    status = db.Column(db.String(80), default='PENDING')
    result = db.Column(db.Float, nullable=True)

# --- 4. Initialize Kafka Producer (with Retry Loop) ---
KAFKA_SERVER = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
CONVERSION_TOPIC = 'conversions'

print("Starting API Service (Producer)...")
print(f"Connecting to Kafka at {KAFKA_SERVER}...")

producer = None
while producer is None:
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_SERVER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka Producer connected!")
    except NoBrokersAvailable:
        print(f"Kafka not ready. Retrying in 5 seconds...")
        time.sleep(5)
    except Exception as e:
        print(f"An unexpected error occurred: {e}. Retrying in 5 seconds...")
        time.sleep(5)


# --- 5. API Route (Updated) ---
@app.route('/api/convert', methods=['POST'])
def handle_conversion():
    """
    Accepts a conversion task, saves it to the DB, and sends to Kafka.
    ---
    (Swagger documentation is the same as before)
    ...
    """
    try:
        data = request.json
        
        # --- 1. Save the new task to the database ---
        new_task = Conversion(
            input_value=float(data.get('input_value')),
            unit_from=data.get('unit_from'),
            unit_to=data.get('unit_to'),
            status='PENDING'
        )
        db.session.add(new_task)
        db.session.commit()
        
        # --- 2. Add the new database ID to the Kafka message ---
        data['task_id'] = new_task.id
        
        # --- 3. Send the message to Kafka ---
        producer.send(CONVERSION_TOPIC, key=data['form_id'].encode('utf-8'), value=data)
        producer.flush() 
        
        # --- 4. Respond to the frontend IMMEDIATELY ---
        return jsonify({"message": f"Conversion task {new_task.id} accepted."}), 202
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Error: {e}"}), 500

# --- 6. Run the Server ---
if __name__ == '__main__':
    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)