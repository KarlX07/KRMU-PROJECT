# Real-Time Fleet Management & Route Optimization

## 1. Project Overview

This project implements a Genetic Algorithm to optimize delivery routes using the Traveling Salesman Problem (TSP) approach. The system minimizes total travel distance, which directly reduces fuel consumption and operational costs in logistics operations.

The backend is built using FastAPI and exposes an API endpoint to compute optimized delivery routes.

---

## 2. Problem Statement

Logistics companies face high operational costs due to inefficient routing and increasing fuel prices. Manual route planning becomes ineffective as delivery points increase, especially in large-scale scenarios.

This project addresses the Traveling Salesman Problem (TSP) using a heuristic approach (Genetic Algorithm) to find near-optimal routes efficiently.

---

## 3. Technology Stack

- Python
- FastAPI
- Uvicorn
- Genetic Algorithm (Selection, Crossover, Mutation)
- GitHub (Version Control)
- Projexa AI (Repository Monitoring)

---

## 4. System Architecture

Driver / GPS Data (Simulated Input)
        ↓
FastAPI Backend
        ↓
Genetic Algorithm Optimization Engine
        ↓
Optimized Route Output
        ↓
Future: Dashboard Visualization

---

## 5. Features Implemented (Mid-Term Status)

- Genetic Algorithm for TSP
- Route distance calculation
- Selection, Crossover, Mutation operations
- FastAPI backend API
- Swagger UI testing interface
- GitHub integration


---


## 6. Setup & Execution Instructions

- Step 1: Install Dependencies
  pip install fastapi uvicorn

- Step 2: Run Backend Server
  uvicorn backend.main:app --reload

- Step 3: Open API Documentation
  http://127.0.0.1:8000/docs

- Step 4: Test Optimization API
  Use POST /optimize-route with JSON input like:

{
"locations": [[10,20], [30,40], [50,25], [60,10]]
}

## 7. Future Scope

  Real-time GPS tracking

  Multi-vehicle optimization

  Fuel analytics

  Live dashboard

  Cloud deployment

## 8. Academic Objective

To understand heuristic search algorithms and apply Genetic Algorithms to real-world logistics optimization problems.

## 6. Setup & Execution Instructions

### Step 1: Install Dependencies
