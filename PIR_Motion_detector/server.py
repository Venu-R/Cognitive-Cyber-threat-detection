from flask import Flask, request, jsonify
import csv
from datetime import datetime
import os

app = Flask(__name__)

CSV_FILE = "pir_logs.csv"

# Ensure CSV file exists with proper headers
if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "motion_detected"])  # Proper header

@app.route('/pir', methods=['POST'])
def log_pir():
    try:
        data = request.get_json()
        motion = data.get("motion_detected")  # Expect "1" or "0" from ESP12E

        # Convert to 1/0 if it comes as string like "Motion Detected"/"No Motion"
        if motion == "Motion Detected":
            motion = 1
        elif motion == "No Motion":
            motion = 0
        elif motion == "1":
            motion = 1
        elif motion == "0":
            motion = 0
        else:
            motion = 0  # default to no motion if unknown

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Write to CSV
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, motion])

        return jsonify({"status": "success", "timestamp": timestamp, "motion_detected": motion}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/pir_logs', methods=['GET'])
def get_pir_logs():
    logs = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            logs.append(row)
    return jsonify(logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
