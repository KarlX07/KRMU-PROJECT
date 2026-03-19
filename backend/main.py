from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.ga_optimizer import genetic_algorithm, calculate_distance
from backend.database import SessionLocal, init_db, RouteHistory

# ----------------------------
# Fixed Delhi Warehouse
# ----------------------------
WAREHOUSE = (28.6139, 77.2090)

# Business Constants
FUEL_PRICE = 90          # ₹ per litre
AVERAGE_SPEED = 40       # km per hour (for ETA calculation)

app = FastAPI()
init_db()

templates = Jinja2Templates(directory="backend/templates")

class LocationInput(BaseModel):
    locations: list


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/optimize-route")
def optimize(data: LocationInput):
    delivery_points = data.locations

    if len(delivery_points) < 2:
        return {"error": "Minimum 2 delivery points required"}

    mid = len(delivery_points) // 2
    truck1_points = delivery_points[:mid]
    truck2_points = delivery_points[mid:]

    def run_truck(points):
        all_points = [WAREHOUSE] + points

        # Naive sequential route (before optimization)
        naive_distance = calculate_distance(all_points)

        # Optimized route
        best_route, best_distance = genetic_algorithm(all_points)

        fuel_rate = 0.5
        fuel_saved = max((naive_distance - best_distance) * fuel_rate, 0)
        cost_saved = fuel_saved * FUEL_PRICE

        eta_hours = best_distance / AVERAGE_SPEED

        return {
            "route": best_route,
            "metrics": {
                "naive_distance": round(naive_distance, 4),
                "optimized_distance": round(best_distance, 4),
                "fuel_saved": round(fuel_saved, 4),
                "cost_saved": round(cost_saved, 2),
                "eta_hours": round(eta_hours, 2)
            }
        }

    truck1 = run_truck(truck1_points)
    truck2 = run_truck(truck2_points)

    total_cost_saved = truck1["metrics"]["cost_saved"] + truck2["metrics"]["cost_saved"]
    total_eta = max(truck1["metrics"]["eta_hours"], truck2["metrics"]["eta_hours"])

    db = SessionLocal()
    new_entry = RouteHistory(
        random_distance=truck1["metrics"]["naive_distance"] + truck2["metrics"]["naive_distance"],
        optimized_distance=truck1["metrics"]["optimized_distance"] + truck2["metrics"]["optimized_distance"],
        fuel_saved=truck1["metrics"]["fuel_saved"] + truck2["metrics"]["fuel_saved"]
    )
    db.add(new_entry)
    db.commit()
    db.close()

    return {
        "warehouse": WAREHOUSE,
        "total_cost_saved": round(total_cost_saved, 2),
        "total_eta": round(total_eta, 2),
        "truck1": truck1,
        "truck2": truck2
    }