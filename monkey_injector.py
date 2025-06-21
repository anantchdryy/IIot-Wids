import time
import pandas as pd
import numpy as np
from pymongo import MongoClient
from feature_extraction import PROTOCOL_CATEGORIES, FLAGS_CATEGORIES

# ───── CONFIG ───────────────────────────────────────────────────
CSV_FILE   = "IIoT_Malware_Timeseries_CLEAN.csv"
MONGO_URI  = "mongodb+srv://anant:Anantislive1@wids.hroqzag.mongodb.net/wids?retryWrites=true&w=majority"
DB_NAME    = "wids"
ANOM_COLL  = "anomalies"
NUM_SAMPLES = 3
# ─────────────────────────────────────────────────────────────────

# Same continuous columns used in feature_extraction
CONT_COLS = [
    "Packet Size", "Packet Length", "Inter-Arrival Time",
    "Flow Duration", "Total Packets", "Total Bytes",
    "Average Packet Size", "Packet Arrival Rate",
    "Payload Entropy", "Flow Entropy",
    "Baseline Deviation", "Packet Size Variance",
    "Known IoC", "C&C Communication", "Data Exfiltration"
]


def build_features(row):
    """
    Build the features dict from a CSV row without running the model.
    """
    # continuous
    cont = {col: float(row[col]) for col in CONT_COLS}
    # protocol one-hot
    proto_val = row["Protocol Type"]
    proto_arr = [1.0 if p == proto_val else 0.0 for p in PROTOCOL_CATEGORIES]
    # flags one-hot
    flags_list = [f.strip() for f in row["Flags"].split(",")]
    flag_arr = [1.0 if f in flags_list else 0.0 for f in FLAGS_CATEGORIES]

    feats = cont.copy()
    feats["Protocol Type (one-hot)"] = proto_arr
    feats["Flags (one-hot)"]       = flag_arr
    return feats


def main():
    # read CSV and sample anomaly rows
    df = pd.read_csv(CSV_FILE)
    samples = df[df["Label"] != "Benign"].sample(NUM_SAMPLES)

    client = MongoClient(MONGO_URI)
    anoms_col = client[DB_NAME][ANOM_COLL]

    for _, row in samples.iterrows():
        label = row["Label"]
        # set probability to 100% since it's from ground-truth
        prob = 1.0
        probs = {label: 1.0}

        record = {
            "timestamp":     time.strftime("%Y-%m-%d %H:%M:%S"),
            "interface":     "csv-inject",
            "label":         label,
            "probability":   prob,
            "probabilities": probs,
            # ground-truth anomalies go here
            "anomaly_families": [label],
            "anomaly_probs":    {label: prob},
            "features":         build_features(row)
        }

        print(f"Injecting anomaly: {label} -> {record}")
        anoms_col.insert_one(record)

    print(f"Done: injected {NUM_SAMPLES} anomalies into {DB_NAME}.{ANOM_COLL}")

if __name__ == "__main__":
    main()
