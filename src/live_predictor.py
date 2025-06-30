import subprocess
import time
import joblib
import numpy as np
from pymongo import MongoClient
from feature_extraction import extract_features_full, PROTOCOL_CATEGORIES, FLAGS_CATEGORIES
import os
from dotenv import load_dotenv

PCAP_FILE        = "temp.pcap"
MODEL_FILE       = "family_detectors.pkl"
CAPTURE_DURATION = 3600  
DEFAULT_INTERFACE = '5'
DEVICE_FILTER = "host 192.168.1.44"

# MongoDB connection
load_dotenv()
user = os.getenv('user')
pw = os.getenv('pw')
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME= os.getenv('DB_NAME')
COLLECTION = os.getenv('COLLECTION')

# Full path to tshark.exe 
TSHARK_CMD = r"C:\Program Files\Wireshark\tshark.exe"

def wait_for_flush(path, tries=6, pause=2):
    last = -1
    for _ in range(tries):
        try:
            sz= os.path.getsize(path)
            if sz == last and sz>0:
                return True
            last = sz
        except FileNotFoundError:
            pass
        time.sleep(pause)
    return False

def list_interfaces():
    """Print available capture interfaces so you can pick one."""
    res = subprocess.run(
        [TSHARK_CMD, "-D"],
        capture_output=True, text=True, check=True
    )
    print("Available interfaces:\n", res.stdout)

def capture_pcap(interface, duration=CAPTURE_DURATION, output=PCAP_FILE, bpf=DEVICE_FILTER):
    """Capture `duration` seconds of traffic into `output`."""
    cmd = [
        TSHARK_CMD,
        "-i", interface,
        "-f", bpf,
        "-a", f"duration:{duration}",
        "-w", output
    ]
    print(f"[+] Capturing {duration}s on {interface} → {output}")
    subprocess.run(cmd, check=True)

def load_model(path=MODEL_FILE):
    """
    Loads your joblib‐dumped dict of CalibratedClassifierCVs:
      { family_name: CalibratedClassifierCV, … }
    """
    return joblib.load(path)

def predict(features, model_dict):
    """
    Given a feature‐vector and a dict of binary classifiers,
    returns (best_label, probabilities_dict).
    
    Each classifier is assumed binary with .classes_ = [0,1],
    so we pull out the probability of class==1 as that family's score.
    """
    arr = np.array(features).reshape(1, -1)
    probs = {}
    for family, clf in model_dict.items():
        p = clf.predict_proba(arr)[0]
        
        pos_idx = list(clf.classes_).index(1)
        probs[family] = float(p[pos_idx])
    
    best = max(probs, key=probs.get)
    return best, probs

def main():
    
    interface = DEFAULT_INTERFACE
    print(f"[+] Using default interface {interface}")

   
    client = MongoClient(MONGO_URI)
    col    = client[DB_NAME][COLLECTION]
    anomalies_col = client[DB_NAME]["anomalies"]

    
    model_dict = load_model()

    print("[*] Starting live capture & prediction loop. Ctrl-C to stop.")
    try:
        while True:
            
            capture_pcap(interface, duration=CAPTURE_DURATION)
            if not wait_for_flush(PCAP_FILE):
                print("[!] PCAP still unstable or empty — skipping this cycle.")
                continue


            feats = extract_features_full(PCAP_FILE)

            
            label, probs = predict(feats, model_dict)
            risk_score   = probs[label]

            
            record = {
                "timestamp":    time.strftime("%Y-%m-%d %H:%M:%S"),
                "interface":    interface,
                "label":        label,
                "probability":   risk_score,
                "probabilities": probs
            }
            col.insert_one(record)
            print(f"[+] {record}")
            benign_p = probs["Benign"]
            hits = [f for f,p in probs.items() if f!="Benign" and p>benign_p]
            if hits:
                anomaly_record = {**record,"anomaly_families": hits,"anomaly_probs":    {f:probs[f] for f in hits},
                                  "features": {
                                      "Packet Size": feats[0],
                                      "Packet Length": feats[1],
                                      "Inter-Arrival Time": feats[2],
                                      "Flow Duration": feats[3],
                                      "Total Packets": feats[4],
                                      "Total Bytes": feats[5],
                                      "Average Packet Size": feats[6],
                                      "Packet Arrival Rate": feats[7],
                                      "Payload Entropy": feats[8],
                                      "Flow Entropy": feats[9],
                                      "Baseline Deviation": feats[10],
                                      "Packet Size Variance": feats[11],
                                      "Known IoC": feats[12],
                                      "C&C Communication": feats[13],
                                      "Data Exfiltration": feats[14],
                                      "Protocol Type (one-hot)": feats[15 : 15 + len(PROTOCOL_CATEGORIES)],
                                      "Flags (one-hot)": feats[15 + len(PROTOCOL_CATEGORIES) :] }
                                  }
                anomalies_col.insert_one(anomaly_record)
                print(f"[!] Anomaly! stored: {anomaly_record}")

          
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")

if __name__ == "__main__":
    main()
