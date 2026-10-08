# 🔐 BioSecure – Biometric Face Authentication System

BioSecure is a web-based biometric authentication system that uses **face recognition** for secure user login. It is built using Flask, OpenCV, LBPH and SQLite.

## 🚀 Features

- 👤 User registration with facial samples
- 📷 Webcam-based face capture
- 🔍 Face detection using Haar Cascade
- 🧠 Face recognition using LBPH
- 🔐 Secure biometric login
- 📊 Authentication dashboard
- 📝 Login history and statistics
- 🗄️ SQLite database integration
- 🌐 Deployable as a Flask web application

## 🛠️ Technologies

- Python 3.11
- Flask
- OpenCV
- LBPH Face Recognition
- NumPy
- SQLite
- HTML, CSS, JavaScript
- Gunicorn

## 🏗️ Architecture

```text
Webcam
   ↓
OpenCV Face Detection
   ↓
Face Preprocessing
   ↓
LBPH Face Recognition
   ↓
SQLite Database
   ↓
Authentication Result
   ↓
Dashboard

⚙️ Run Locally
git clone https://github.com/Nitish-jm25/biometric-login-system.git
cd biometric-login-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

Open:
http://127.0.0.1:5000

🌐 Deployment
The application can be deployed using Render.
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

⚠️ Note
This project is developed for academic and educational purposes. Production biometric systems should include encryption, liveness detection, anti-spoofing, secure biometric storage and stronger authentication controls.
👨‍💻 Author
Nitish Raj J M
B.Tech Artificial Intelligence & Data Science
Velammal Engineering College
⭐ If you find this project useful, consider starring the repository.
