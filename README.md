# 🚚 Real-Time Fleet Management & Route Optimization System

## 📌 Project Overview

This project is a **real-time fleet management and route optimization
system** that combines **Genetic Algorithms, K-Means clustering, and
OSRM routing** to optimize delivery routes for multiple vehicles.

It not only computes optimal delivery paths but also provides **live GPS
tracking, real-time updates, and intelligent route monitoring**, making
it a near production-level logistics solution.

------------------------------------------------------------------------

## ❗ Problem Statement

Logistics companies face:

-   High fuel costs due to inefficient routing\
-   Poor scalability in manual route planning\
-   Lack of real-time monitoring of delivery vehicles\
-   Inability to handle multi-vehicle routing efficiently

This project solves these issues by combining **AI-based optimization
with real-time tracking and visualization**.

------------------------------------------------------------------------

## 🚀 Key Features

### 🔹 Optimization Engine

-   Genetic Algorithm for solving TSP (Traveling Salesman Problem)
-   K-Means clustering for multi-truck route distribution
-   Near-optimal route generation

### 🔹 Real-Time System

-   Live GPS tracking using WebSockets
-   Driver location updates in real time
-   Vehicle status monitoring (active/idle)

### 🔹 Smart Routing

-   OSRM integration for real road distance and routes
-   Accurate ETA calculation
-   Real-world path visualization

### 🔹 Visualization

-   Interactive map using Leaflet.js
-   Animated truck movement
-   Multi-route display with different colors

### 🔹 Intelligent Features

-   Route deviation detection
-   Fuel and cost savings estimation
-   Performance metrics

------------------------------------------------------------------------

## 🛠 Technology Stack

### Backend

-   Python
-   FastAPI
-   Uvicorn
-   WebSockets
-   Requests

### Frontend

-   HTML, CSS, JavaScript
-   Leaflet.js

### Algorithms

-   Genetic Algorithm
-   K-Means Clustering
-   OSRM Routing

------------------------------------------------------------------------

## 🏗 System Architecture

Driver (Mobile GPS) ↓ WebSocket (Live Data) ↓ FastAPI Backend ↓
Optimization Engine (GA + K-Means) ↓ OSRM Routing Engine ↓ Frontend
Dashboard

------------------------------------------------------------------------

## ⚙️ Setup & Execution

### Install Dependencies

pip install fastapi uvicorn requests scikit-learn

### Run Server

uvicorn backend.main:app --reload

### Open

http://127.0.0.1:8000

------------------------------------------------------------------------

## 📈 Future Enhancements

-   Traffic prediction
-   Dynamic routing
-   Driver scoring
-   Cloud deployment

------------------------------------------------------------------------

## 🎯 Conclusion

A full-stack intelligent fleet system combining AI, real-time tracking,
and optimization.
