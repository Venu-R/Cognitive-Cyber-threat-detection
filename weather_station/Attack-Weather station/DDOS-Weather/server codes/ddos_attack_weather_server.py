from flask import Flask, request
import csv
from datetime import datetime

app = Flask(__name__)
FILENAME = 'attack_weather_ddos_log.csv'

# Ensure CSV has headers
with open(FILENAME, 'a', newline='') as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow([
            'timestamp',
            'device_id',
            'temperature',
            'humidity',
            'motion',
            'status',
            'error_message'
        ])

def is_weird(value, sensor_type):
    # Acceptable DHT22 temperature: 0 - 50°C (adjust as per real range)
    # Acceptable DHT22 humidity: 20 - 90%
    try:
        if sensor_type == "temperature":
            v = float(value)
            if v < 0 or v > 50:
                return True
        if sensor_type == "humidity":
            v = float(value)
            if v < 20 or v > 90:
                return True
    except Exception:
        # Non-numeric value is weird
        return True
    # Strings like 'error', 'N/A', '?' are weird
    if isinstance(value, str) and value.strip().lower() in ['error', 'n/a', '?']:
        return True
    return False

@app.route('/log', methods=['POST'])
def log_data():
    data = request.json
    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
    device_id = data.get('device_id', 'station1')
    temperature = data.get('temperature', 'N/A')
    humidity = data.get('humidity', 'N/A')
    motion = data.get('motion', 'N/A')

    temp_weird = is_weird(temperature, "temperature")
    hum_weird = is_weird(humidity, "humidity")
    
    if temp_weird or hum_weird:
        status = 'error'
        error_message = 'Invalid sensor reading: temperature/humidity out of range or corrupted'
        result = {'status': status, 'errorMessage': error_message}
    else:
        status = 'OK'
        error_message = '-'
        result = {'status': status}

    # Log to CSV
    row = [
        timestamp,
        device_id,
        temperature,
        humidity,
        motion,
        status,
        error_message
    ]
    with open(FILENAME, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    print("LOGGED: " + str(row))

    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
