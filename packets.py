from scapy.all import rdpcap
import numpy as np
import joblib
model = joblib.load('wids_risk_model.pkl')
def extract_features(pcap_file):
    packets = rdpcap(pcap_file)
    total_packets = len(packets)
    avg_size = np.mean([len(pkt) for pkt in packets]) if total_packets > 0 else 0
    tcp_count = len([pkt for pkt in packets if pkt.haslayer('TCP')])
    udp_count = len([pkt for pkt in packets if pkt.haslayer('UDP')])
    icmp_count = len([pkt for pkt in packets if pkt.haslayer('ICMP')])
    unique_dst_ips = len(set(pkt[1].dst for pkt in packets if hasattr(pkt[1], 'dst')))

    feature_vector = np.array([
        total_packets,
        avg_size,
        tcp_count,
        udp_count,
        icmp_count,
        unique_dst_ips
    ]).reshape(1, -1)
    
    return feature_vector
features = extract_features('out.pcap')
print("Features:", features)
prediction = model.predict(features)[0]
print(f'Predicted risk score: {prediction:.4f}')
