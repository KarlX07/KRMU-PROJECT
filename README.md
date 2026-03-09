# Real-Time Fleet Management & Route Optimization

## Project Description
This project implements a Genetic Algorithm to solve the Traveling Salesman Problem (TSP) for optimizing delivery routes.

## Features
- Genetic Algorithm (Selection, Crossover, Mutation)
- FastAPI backend
- Route optimization endpoint
- Swagger UI testing

## Tech Stack
- Python
- FastAPI
- Uvicorn

## API Endpoint
POST /optimize-route

Input:
{
  "locations": [[x1, y1], [x2, y2], ...]
}

Output:
{
  "optimized_route": [...],
  "optimized_distance": value
}

## Objective
To reduce total travel distance and fuel consumption using heuristic optimization techniques.
