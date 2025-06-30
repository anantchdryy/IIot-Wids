IIoT-WIDS
Wireless Intrusion Detection System for Industrial IoT Networks
Live packet capture → feature extraction → ML prediction → React dashboard

Features

Live packet capture using TShark or custom Python scripts

Modular feature extraction pipeline in Python

Real-time anomaly classification with a pretrained XGBoost model

Flask-based REST API (/api/start, /api/stop, /api/latest)

React frontend with live anomaly visualization

Repository Structure

IIoT-WIDS/
├── README.md
├── .gitignore
├── requirements.txt
├── src/ (Python backend)
│ ├── app.py (Flask API)
│ ├── live_predictor.py (Capture loop + ML inference)
│ ├── feature_extraction.py
│ └── packets.py
├── notebooks/
│ └── WIDS_new_model.ipynb (Model training and eval)
└── ui/ (React frontend)
├── package.json
├── package-lock.json
└── src/
├── index.js
├── App.js
├── home.css
└── ...

Requirements

Python 3.8+

Node.js 14+ and npm

MongoDB (Atlas or local)

Wireshark with tshark in PATH

(Optional) Git

Setup

Clone the repo
git clone https://github.com/anantchdryy/IIot-Wids.git
cd IIot-Wids

Backend (Python)
python3 -m venv venv

Activate virtual environment:

macOS/Linux: source venv/bin/activate

Windows: .\venv\Scripts\Activate

Install dependencies:
pip install --upgrade pip
pip install -r requirements.txt

Frontend (React)
cd ui
npm install
cd ..

Configuration
Create a .env file in the root directory with the following:

MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/wids?retryWrites=true&w=majority
MONGO_DB=wids
MONGO_COLLECTION=predictions

To modify anomaly detection thresholds, edit src/thresholds.json

Usage

Start Flask API
source venv/bin/activate (or activate for Windows)
python src/app.py
Flask API will run at http://localhost:5000

Start Packet Capture & Prediction (in separate terminal with venv activated)
python src/live_predictor.py

Launch Frontend
cd ui
npm start
Visit http://localhost:3000 in your browser

Jupyter Notebooks
Model training notebook:
notebooks/WIDS_new_model.ipynb
Run using:
jupyter lab notebooks/WIDS_new_model.ipynb

Contributing
git checkout -b feature/your-feature
git add .
git commit -m "feat: description"
git push origin feature/your-feature
Open a Pull Request to main

License
MIT License

