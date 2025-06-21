import pandas as pd
import pyshark
import numpy as np
from collections import Counter
from math import log2

# Automatically load categories from your training CSV
CSV_PATH = "IIoT_Malware_Timeseries_CLEAN.csv"
df = pd.read_csv(CSV_PATH)
PROTOCOL_CATEGORIES = sorted(df['Protocol Type'].dropna().unique().tolist())
FLAGS_CATEGORIES    = sorted(df['Flags'].dropna().unique().tolist())


def one_hot(value, categories):
    """Simple one-hot encode a single value against a fixed category list."""
    return [1 if value == cat else 0 for cat in categories]


def shannon_entropy(byte_arr: np.ndarray) -> float:
    """Compute Shannon entropy of a 1-D array of byte values."""
    if byte_arr.size == 0:
        return 0.0
    counts = np.bincount(byte_arr, minlength=256)
    probs = counts[counts>0] / byte_arr.size
    return float(-np.sum(probs * np.log2(probs)))


def extract_features_full(pcap_file: str) -> list:
    """
    Read PCAP, compute 15 numerical features + one-hot most-common Protocol Type & Flags.
    Returns a flat list of length == 15 + len(PROTOCOL_CATEGORIES) + len(FLAGS_CATEGORIES).
    """
    # Capture packets
    cap = pyshark.FileCapture(pcap_file, keep_packets=False)
    times, frame_lens, ip_lens = [], [], []
    protocols, flags_list = [], []
    payload_bytes = []

    for pkt in cap:
        try:
            t = float(pkt.sniff_timestamp)
            times.append(t)

            fl = int(pkt.length)
            frame_lens.append(fl)

            # IP length if present
            if hasattr(pkt, 'ip'):
                ip_lens.append(int(pkt.ip.len))
            else:
                ip_lens.append(fl)

            # Protocol & Flags
            proto = pkt.highest_layer.upper()
            protocols.append(proto)
            if 'TCP' in pkt:
                flags_list.append(pkt.tcp.flags_str.upper())
                raw = getattr(pkt.tcp, 'payload', None)
                if raw:
                    hexstr = raw.replace(':', '')
                    try:
                        payload_bytes.extend(bytes.fromhex(hexstr))
                    except ValueError:
                        pass
        except Exception:
            continue
    cap.close()

    # If no packets, return zeros
    total_len = 15 + len(PROTOCOL_CATEGORIES) + len(FLAGS_CATEGORIES)
    if not times:
        return [0.0] * total_len

    # --- Numerical features ---
    flow_duration = max(times) - min(times)
    total_packets = len(frame_lens)
    total_bytes   = sum(frame_lens)
    avg_pkt_size  = float(np.mean(frame_lens))
    pkt_arr_rate  = total_packets / (flow_duration if flow_duration>0 else 1.0)

    # Inter-arrival times
    sorted_t = sorted(times)
    iats = np.diff(sorted_t) if total_packets>1 else np.array([0.0])
    mean_iat = float(np.mean(iats))

    # Packet-size stats
    packet_size_feat   = float(max(frame_lens))
    packet_length_feat = float(np.mean(ip_lens))
    pkt_size_variance  = float(np.var(frame_lens))

    # Entropies
    payload_entropy = shannon_entropy(np.array(payload_bytes, dtype=np.uint8))
    proto_counts  = Counter(protocols)
    total_proto   = sum(proto_counts.values())
    flow_entropy  = float(-sum((c/total_proto)*log2(c/total_proto) for c in proto_counts.values()))

    # Baseline deviation: CV of IATs
    if mean_iat>0:
        baseline_deviation = float(np.std(iats) / mean_iat)
    else:
        baseline_deviation = 0.0

    # Binary indicators (implement your IOC/C&C/exfil logic)
    known_ioc  = 0
    cc_comm    = 0
    data_exfil = 0

    numerical_features = [
        packet_size_feat,
        packet_length_feat,
        mean_iat,
        flow_duration,
        total_packets,
        total_bytes,
        avg_pkt_size,
        pkt_arr_rate,
        payload_entropy,
        flow_entropy,
        baseline_deviation,
        pkt_size_variance,
        known_ioc,
        cc_comm,
        data_exfil
    ]

    # One-hot encode most-common categories
    most_proto = Counter(protocols).most_common(1)[0][0]
    most_flag  = Counter(flags_list).most_common(1)[0][0] if flags_list else None

    proto_vec = one_hot(most_proto, PROTOCOL_CATEGORIES)
    flag_vec  = one_hot(most_flag,    FLAGS_CATEGORIES)

    return numerical_features + proto_vec + flag_vec