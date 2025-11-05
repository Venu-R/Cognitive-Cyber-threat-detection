from flask import Flask, request
import csv

app = Flask(__name__)
FILENAME = 'attack_weather_spoof_log.csv'

# Ensure CSV has headers (no timestamp, no status, no error_message)
with open(FILENAME, 'a', newline='') as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow([
            'device_id',
            'temperature',
            'humidity',
            'motion'
        ])

@app.route('/log', methods=['POST'])
def log_data():
    data = request.json
    device_id = data.get('device_id', 'station1')
    temperature = data.get('temperature', 'N/A')
    humidity = data.get('humidity', 'N/A')
    motion = data.get('motion', 'N/A')

    # Log to CSV (no timestamp, status, error fields)
    row = [
        device_id,
        temperature,
        humidity,
        motion
    ]
    with open(FILENAME, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
    print("LOGGED: " + str(row))

    return {"status": "OK"}  # Always return OK for spoofing experiment

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
