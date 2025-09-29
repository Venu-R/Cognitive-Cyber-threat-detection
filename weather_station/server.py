from flask import Flask, request, jsonify
import csv
from datetime import datetime
import os

app = Flask(__name__)

CSV_FILE = "weather_logs.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "temperature", "humidity"])

@app.route('/log', methods=['POST'])
def log_data():
    try:
        data = request.get_json()

        temperature = data.get("temperature")
        humidity = data.get("humidity")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, humidity, temperature])

        return jsonify({"status": "success", "timestamp": timestamp}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/logs', methods=['GET'])
def get_logs():
    """ Endpoint to read logs as JSON (optional) """
    logs = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            logs.append(row)
    return jsonify(logs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)