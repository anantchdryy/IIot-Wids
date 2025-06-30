from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import subprocess, os, signal
import certifi
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME= os.getenv('DB_NAME')
COL_PRED = os.getenv('COLLECTION')
SCRIPT     = os.path.abspath("live_predictor.py")

client = MongoClient(MONGO_URI,tls = True, tlsCAFile=certifi.where())
col    = client[DB_NAME][COL_PRED]
col_anomalies = client[DB_NAME]['anomalies']

proc = None

@app.route('/api/start', methods=['POST'])
def start():
    global proc
    if proc is None or proc.poll() is not None:
        proc = subprocess.Popen(['python', SCRIPT])
        return jsonify({'status':'started'})
    return jsonify({'error':'already running'}), 400

@app.route('/api/stop', methods=['POST'])
def stop():
    global proc
    if proc and proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
        proc = None
        return jsonify({'status':'stopped'})
    return jsonify({'error':'not running'}), 400

@app.route('/api/latest', methods=['GET'])
def latest():
    doc = col.find_one(sort=[('timestamp', -1)])
    if not doc:
        return jsonify({'error':'no data'}), 404
    return jsonify({
      'timestamp':   doc['timestamp'],
      'label':       doc['label'],
      'probability': doc['probability'],
      'probabilities': doc['probabilities']
    })

@app.route('/api/anomalies', methods=['GET']) 
def anomalies():
    print("[DEBUG] /api/anomalies called")
    docs = list(col_anomalies.find().sort('timestamp', -1))
    print(f"[DEBUG] found {len(docs)} anomaly docs")
    for d in docs:
        d['_id'] = str(d['_id'])
    return jsonify(docs) 

if __name__ == '__main__':
    app.run(port=5000, debug=True) #Run the app locally on the port 5000
