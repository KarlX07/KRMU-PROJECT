<div align="center">

# 🚚 Real-Time Fleet Management & Route Optimization System

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet.js-199900?style=for-the-badge&logo=leaflet&logoColor=white)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-orange?style=for-the-badge)

**A near production-level intelligent logistics system combining Genetic Algorithms, real-time WebSocket tracking, and OSRM-based road routing.**

*Major Project — B.Sc. Data Science (Sem VI) | K.R. Mangalam University, April 2026*

[🌐 Live Demo](https://real-time-fleet-management-and-route.onrender.com) &nbsp;|&nbsp; [📄 Report](./report.pdf) &nbsp;|&nbsp; [⚡ Quick Start](#️-setup--execution)

</div>

---

## 📌 Project Overview

This project is a **real-time fleet management and route optimization system** that combines **Genetic Algorithms**, **K-Means clustering**, and **OSRM routing** to optimize delivery routes for multiple vehicles.

It not only computes optimal delivery paths but also provides **live GPS tracking**, **real-time updates**, and **intelligent route monitoring** — making it a near production-level logistics solution.

---

## ❗ Problem Statement

Logistics companies face:

- 🔴 High fuel costs due to inefficient routing
- 🔴 Poor scalability in manual route planning
- 🔴 Lack of real-time monitoring of delivery vehicles
- 🔴 Inability to handle multi-vehicle routing efficiently

This project solves these issues by combining **AI-based optimization** with **real-time tracking** and **visualization**.

---

## 🚀 Key Features

### 🔹 Optimization Engine
- Genetic Algorithm for solving TSP (Traveling Salesman Problem)
- K-Means clustering for multi-truck route distribution
- Near-optimal route generation with **20–28% distance reduction**

### 🔹 Real-Time System
- Live GPS tracking using WebSockets
- Driver location updates in real time
- Vehicle status monitoring (Active / Idle)

### 🔹 Smart Routing
- OSRM integration for real road distances and routes
- Accurate ETA calculation
- Real-world path visualization on interactive map

### 🔹 Visualization
- Interactive map using Leaflet.js
- Animated truck movement simulation
- Multi-route display with different neon colors per truck

### 🔹 Intelligent Features
- Geofencing — auto-detects arrival within **50 meters** of delivery point
- Fuel and cost savings estimation
- Optimization history with performance metrics
- JWT-based role authentication (Admin / Driver)

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, Uvicorn, WebSockets |
| **Database** | SQLite + SQLAlchemy |
| **Authentication** | JWT (python-jose) + sha256_crypt |
| **Frontend** | HTML, CSS, Vanilla JavaScript |
| **Maps & Charts** | Leaflet.js, Chart.js |
| **Algorithms** | Genetic Algorithm, K-Means Clustering |
| **Routing Engine** | OSRM (OpenStreetMap) |
| **Deployment** | Render.com |

---

## 🏗 System Architecture

```
Driver Mobile App (GPS)
        ↓
WebSocket — Live Location Data
        ↓
FastAPI Backend (Python)
        ↓
Optimization Engine (GA + K-Means)
        ↓
OSRM Routing Engine (Real Roads)
        ↓
Admin Dashboard (Leaflet.js Map)
```

---

## 📁 Project Structure

```
KRMU-PROJECT/
└── backend/
    ├── templates/
    │   ├── index.html        →  Route Optimizer
    │   ├── dashboard.html    →  Admin Dashboard
    │   ├── driver.html       →  Driver PWA App
    │   └── login.html        →  Login Page
    ├── auth.py               →  JWT Authentication
    ├── database.py           →  SQLite Models
    ├── ga_optimizer.py       →  Genetic Algorithm Core
    ├── main.py               →  FastAPI Server
    └── __init__.py
```

---

## ⚙️ Setup & Execution

### 1. Install Dependencies
```bash
pip install fastapi uvicorn requests scikit-learn sqlalchemy python-jose[cryptography] passlib
```

### 2. Run Server
```bash
uvicorn backend.main:app --reload
```

### 3. Open in Browser
```
http://127.0.0.1:8000
```

> ⚠️ Use **Chrome** — Edge blocks cookies on localhost

### 🔐 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Driver | `driver1` | `driver123` |
| Driver | `driver2` | `driver456` |

---

## 📊 Results

| Instance | Points | Trucks | Manual (km) | Optimized (km) | Saved |
|----------|--------|--------|-------------|----------------|-------|
| Small | 15 | 3 | 185 | 142 | **23.2%** |
| Medium | 40 | 5 | 465 | 338 | **27.3%** |
| Large | 80 | 8 | 920 | 712 | **22.6%** |

- ⚡ Real-time WebSocket latency: **180–450 ms**
- 🧬 GA convergence: **200–300 generations**
- 📱 PWA installable on any Android/iOS device

---

## 📈 Future Enhancements

- [ ] Live traffic prediction integration
- [ ] Dynamic re-routing during active delivery
- [ ] Driver performance scoring system
- [ ] Vehicle capacity and time-window constraints
- [ ] Multi-depot support
- [ ] Advanced analytics with carbon footprint tracking


---

## 🎯 Conclusion

A full-stack intelligent fleet system combining **AI-based route optimization**, **real-time GPS tracking**, and **progressive web app** technology — delivering a practical, affordable, and scalable solution for small and medium logistics companies in India.

---

<div align="center">

**⭐ Star this repo if you found it useful!**

*K.R. Mangalam University — Department of Computer Science & Engineering, SOET*

</div>
