from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func

from backend.ga_optimizer import genetic_algorithm, calculate_distance, generate_random_route
from backend.database import SessionLocal, init_db, RouteHistory

# ----------------------------
# Fixed Delhi Warehouse
# ----------------------------
WAREHOUSE = (28.6139, 77.2090)

app = FastAPI()

# Initialize database
init_db()

# Templates setup
templates = Jinja2Templates(directory="backend/templates")


class LocationInput(BaseModel):
    locations: list


# ----------------------------
# Home Page (UI)
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ----------------------------
# Optimization API (2 Trucks)
# ----------------------------
@app.post("/optimize-route")
def optimize(data: LocationInput):
    delivery_points = data.locations

    if len(delivery_points) < 2:
        return {"error": "Minimum 2 delivery points required"}

    # Split delivery points into 2 trucks
    mid = len(delivery_points) // 2
    truck1_points = delivery_points[:mid]
    truck2_points = delivery_points[mid:]

    def run_truck(points):
        all_points = [WAREHOUSE] + points

        random_route = generate_random_route(all_points)
        random_distance = calculate_distance(random_route)

        best_route, best_distance = genetic_algorithm(all_points)

        fuel_rate = 0.2
        random_fuel = random_distance * fuel_rate
        optimized_fuel = best_distance * fuel_rate

        return {
            "route": best_route,
            "metrics": {
                "random_distance": random_distance,
                "optimized_distance": best_distance,
                "distance_saved": random_distance - best_distance,
                "fuel_saved": random_fuel - optimized_fuel
            }
        }

    truck1 = run_truck(truck1_points)
    truck2 = run_truck(truck2_points)

    # Combine metrics for database storage
    total_random = truck1["metrics"]["random_distance"] + truck2["metrics"]["random_distance"]
    total_optimized = truck1["metrics"]["optimized_distance"] + truck2["metrics"]["optimized_distance"]
    total_fuel_saved = truck1["metrics"]["fuel_saved"] + truck2["metrics"]["fuel_saved"]

    # Save combined optimization to database
    db = SessionLocal()

    new_entry = RouteHistory(
        random_distance=total_random,
        optimized_distance=total_optimized,
        fuel_saved=total_fuel_saved
    )

    db.add(new_entry)
    db.commit()
    db.close()

    return {
        "warehouse": WAREHOUSE,
        "truck1": truck1,
        "truck2": truck2
    }


# ----------------------------
# Route History API
# ----------------------------
@app.get("/route-history")
def get_route_history():
    db = SessionLocal()

    records = db.query(RouteHistory).order_by(RouteHistory.timestamp.desc()).all()

    history = []
    for record in records:
        history.append({
            "id": record.id,
            "random_distance": record.random_distance,
            "optimized_distance": record.optimized_distance,
            "fuel_saved": record.fuel_saved,
            "timestamp": record.timestamp
        })

    db.close()
    return history


# ----------------------------
# Dashboard (Analytics)
# ----------------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()

    records = db.query(RouteHistory).order_by(RouteHistory.timestamp.desc()).all()

    total_runs = len(records)
    total_fuel_saved = sum(r.fuel_saved for r in records)

    avg_distance_saved = 0
    if total_runs > 0:
        avg_distance_saved = sum(
            r.random_distance - r.optimized_distance
            for r in records
        ) / total_runs

    db.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "records": records,
        "total_runs": total_runs,
        "total_fuel_saved": round(total_fuel_saved, 2),
        "avg_distance_saved": round(avg_distance_saved, 2)
    })