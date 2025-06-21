IIoT WIDS
A Wireless Intrusion Detection System for Industrial IoT networks
Live packet capture → feature extraction → ML prediction → React dashboard

🚀 Features
Live packet capture using tshark or custom Python scripts

Feature extraction pipeline in Python

Real-time anomaly prediction with a pretrained XGBoost model

Flask REST API endpoints (/api/start, /api/stop, /api/latest)

React + CSS frontend for live visualization

📁 Repository Structure
csharp
Copy
Edit
IIot-Wids/
├── README.md
├── .gitignore
├── requirements.txt
├── src/                     # Python backend
│   ├── app.py               # Flask API
│   ├── live_predictor.py    # capture & prediction loop
│   ├── feature_extraction.py
│   └── packets.py
├── notebooks/               # Jupyter notebooks
│   └── WIDS_new_model.ipynb
└── ui/                      # React frontend
    ├── package.json
    ├── package-lock.json
    └── src/
        ├── index.js
        ├── App.js
        ├── home.css
        └── …
⚙️ Prerequisites
Python 3.8+

Node.js 14+ & npm

MongoDB (Atlas or local)

Wireshark/tshark installed and on your PATH

(Optional) Git for version control

🔧 Installation
Clone the repo

bash
Copy
Edit
git clone https://github.com/anantchdryy/IIot-Wids.git
cd IIot-Wids
Backend setup

bash
Copy
Edit
python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows PowerShell
.\venv\Scripts\Activate
pip install --upgrade pip
pip install -r requirements.txt
Frontend setup

bash
Copy
Edit
cd ui
npm install
cd ..
🔑 Configuration
Copy or create a .env file in the root with:

ini
Copy
Edit
MONGO_URI="mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/wids?retryWrites=true&w=majority"
DB_NAME="wids"
To adjust anomaly thresholds, edit src/thresholds.json.

🎬 Usage
Start the Flask API

bash
Copy
Edit
cd IIot-Wids
source venv/bin/activate       # or Activate on Windows
python src/app.py
The API will run at http://localhost:5000.

Launch the live predictor
(in a new terminal, with venv active)

bash
Copy
Edit
python src/live_predictor.py
Run the React dashboard

bash
Copy
Edit
cd ui
npm start
Open http://localhost:3000 in your browser.

📊 Jupyter Notebooks
Model exploration & training lives in notebooks/WIDS_new_model.ipynb.
Start it with:

nginx
Copy
Edit
jupyter lab notebooks/WIDS_new_model.ipynb
🤝 Contributing
Fork this repo

Create a feature branch:

bash
Copy
Edit
git checkout -b feature/your-feature
Commit your changes & push:

sql
Copy
Edit
git add .
git commit -m "feat: description"
git push origin feature/your-feature
Open a Pull Request against main

📄 License
This project is licensed under the MIT License.
