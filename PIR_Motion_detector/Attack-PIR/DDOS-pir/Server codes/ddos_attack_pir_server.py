from flask import Flask, request
import csv
from datetime import datetime

app = Flask(__name__)
FILENAME = 'pir_attack_ddos_log.csv'

# Ensure CSV file has headers
with open(FILENAME, 'a', newline='') as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow([
            'timestamp',
            'device_id',
            'temperature',
            'humidity',
            'motion_detected',
            'status',
            'error_message'
        ])

def is_valid_motion(value):
    return str(value) in ['0', '1', '-1']

@app.route('/pir', methods=['POST'])
def pir_log():
    data = request.json
    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')

    device_id = data.get('device_id', 'pir_motion_detector_01')
    motion = data.get('motion_detected', 'N/A')

    # Validate motion value
    if not is_valid_motion(motion):
        status = 'error'
        error_message = f'Invalid motion_detected value: {motion}'
    elif motion == '-1':  # Automatically flag '-1' as error/malicious
        status = 'error'
        error_message = 'malicious activity'
    else:
        status = data.get('status', 'OK')
        error_message = data.get('error_message', '-')

    # Temperature and humidity are fixed as N/A for PIR sensor
    temperature = 'N/A'
    humidity = 'N/A'

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

    return {"status": status, "error_message": error_message}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
