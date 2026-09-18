import numpy as np
import pandas as pd
import os

def generate_sample_dataset(filepath="data/sample_network_traffic.csv", n_samples=1500):
    np.random.seed(42)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    classes = ["Normal", "DDoS", "Port Scan", "Brute Force", "Botnet"]
    proportions = [0.45, 0.20, 0.15, 0.10, 0.10]
    
    records = []
    
    for cls, prop in zip(classes, proportions):
        count = int(n_samples * prop)
        for _ in range(count):
            if cls == "Normal":
                flow_duration = np.random.uniform(500, 45000)
                total_fwd = np.random.randint(4, 35)
                total_bwd = np.random.randint(3, 30)
                flow_bytes_per_sec = np.random.uniform(5000, 150000)
                flow_packets_per_sec = np.random.uniform(20, 250)
                packet_length_mean = np.random.uniform(400, 1100)
                packet_length_std = np.random.uniform(50, 250)
                syn_flag_count = np.random.choice([0, 1], p=[0.7, 0.3])
                ack_flag_count = np.random.randint(3, 28)
                urg_flag_count = 0
                dest_port = np.random.choice([80, 443, 53, 8080], p=[0.4, 0.45, 0.1, 0.05])
                protocol = np.random.choice(["TCP", "UDP"], p=[0.85, 0.15])
            
            elif cls == "DDoS":
                flow_duration = np.random.uniform(50, 1500)
                total_fwd = np.random.randint(150, 1200)
                total_bwd = np.random.randint(0, 3)
                flow_bytes_per_sec = np.random.uniform(800000, 6000000)
                flow_packets_per_sec = np.random.uniform(3000, 18000)
                packet_length_mean = np.random.uniform(40, 95)
                packet_length_std = np.random.uniform(5, 25)
                syn_flag_count = np.random.randint(80, 600)
                ack_flag_count = np.random.choice([0, 1], p=[0.9, 0.1])
                urg_flag_count = 0
                dest_port = np.random.choice([80, 443, 53, 8080], p=[0.5, 0.3, 0.1, 0.1])
                protocol = "TCP"

            elif cls == "Port Scan":
                flow_duration = np.random.uniform(1, 40)
                total_fwd = np.random.randint(1, 3)
                total_bwd = 0
                flow_bytes_per_sec = np.random.uniform(200, 2500)
                flow_packets_per_sec = np.random.uniform(800, 3500)
                packet_length_mean = np.random.uniform(32, 64)
                packet_length_std = 0
                syn_flag_count = 1
                ack_flag_count = 0
                urg_flag_count = 0
                dest_port = np.random.randint(20, 9999)
                protocol = "TCP"

            elif cls == "Brute Force":
                flow_duration = np.random.uniform(3000, 12000)
                total_fwd = np.random.randint(30, 80)
                total_bwd = np.random.randint(25, 75)
                flow_bytes_per_sec = np.random.uniform(8000, 45000)
                flow_packets_per_sec = np.random.uniform(40, 120)
                packet_length_mean = np.random.uniform(80, 220)
                packet_length_std = np.random.uniform(15, 60)
                syn_flag_count = np.random.randint(2, 6)
                ack_flag_count = np.random.randint(25, 70)
                urg_flag_count = 0
                dest_port = np.random.choice([22, 21, 3389], p=[0.65, 0.25, 0.10])
                protocol = "TCP"

            elif cls == "Botnet":
                flow_duration = np.random.uniform(15000, 80000)
                total_fwd = np.random.randint(8, 25)
                total_bwd = np.random.randint(6, 20)
                flow_bytes_per_sec = np.random.uniform(1200, 12000)
                flow_packets_per_sec = np.random.uniform(5, 30)
                packet_length_mean = np.random.uniform(150, 450)
                packet_length_std = np.random.uniform(80, 220)
                syn_flag_count = np.random.choice([0, 1])
                ack_flag_count = np.random.randint(5, 18)
                urg_flag_count = np.random.choice([0, 1], p=[0.85, 0.15])
                dest_port = np.random.choice([6667, 1337, 8000, 4444, 9001])
                protocol = np.random.choice(["TCP", "UDP"], p=[0.75, 0.25])

            records.append({
                "flow_duration": round(flow_duration, 2),
                "total_fwd_packets": int(total_fwd),
                "total_bwd_packets": int(total_bwd),
                "flow_bytes_per_sec": round(flow_bytes_per_sec, 2),
                "flow_packets_per_sec": round(flow_packets_per_sec, 2),
                "packet_length_mean": round(packet_length_mean, 2),
                "packet_length_std": round(packet_length_std, 2),
                "syn_flag_count": int(syn_flag_count),
                "ack_flag_count": int(ack_flag_count),
                "urg_flag_count": int(urg_flag_count),
                "destination_port": int(dest_port),
                "protocol_type": protocol,
                "label": cls
            })

    df = pd.DataFrame(records)
    # Shuffle
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.to_csv(filepath, index=False)
    print(f"Generated {len(df)} records in {filepath}")
    print("Class distribution:\n", df['label'].value_counts())
    return df

if __name__ == "__main__":
    generate_sample_dataset()
