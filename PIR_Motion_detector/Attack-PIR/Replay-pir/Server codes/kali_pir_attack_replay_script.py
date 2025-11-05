import pandas as pd
import numpy as np
import random
import requests
import time

# === SET THESE ===
normal_file = 'pir_logs.csv'    # or 'weather_logs.csv'
server_url = 'http://127.0.0.1:5000/your-endpoint'  # Change to your actual server endpoint/port

# ================

df = pd.read_csv(normal_file)

n_blocks = random.randint(4, 5)
min_block_size = 50
max_block_size = 100
blocks = []

max_start = len(df) - max_block_size

# Pick random blocks
for _ in range(n_blocks):
    block_size = random.randint(min_block_size, max_block_size)
    start_idx = random.randint(0, max_start)
    block = df.iloc[start_idx:start_idx+block_size].copy()
    block['attack_type'] = 'replay'
    blocks.append(block)

try:
    print('Sending replay attack data... Press Ctrl+C to stop.')
    while True:
        chosen_block = random.choice(blocks)
        for _, row in chosen_block.iterrows():
            # Convert row to dict and remove attack_type for sending if server doesn't expect it
            data = row.drop('attack_type').to_dict()
            try:
                resp = requests.post(server_url, json=data, timeout=2)
                print(f'Sent: {data} | {resp.status_code}')
            except Exception as e:
                print('Error:', e)
            time.sleep(0.1)  # adjust delay if needed
except KeyboardInterrupt:
    print('\nStopped replay attack streaming.')
