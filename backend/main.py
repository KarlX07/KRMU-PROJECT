from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import json
import math

from backend.ga_optimizer import genetic_algorithm, calculate_distance
from backend.database import SessionLocal, init_db, RouteHistory, Vehicle

app = FastAPI(title="Fleet Intelligence System")
init_db()

templates = Jinja2Templates(directory="templates")

WAREHOUSE = (28.6139, 77.2090)
FUEL_PRICE = 90
FUEL_RATE = 0.12
AVERAGE_SPEED = 45

class LocationInput(BaseModel):
    locations: list
    num_trucks: int = 2   # Default 2 trucks

# WebSocket
driver_connections: dict = {}
dashboard_connections = []

# ==================== WebSocket Endpoints ====================

@app.websocket("/ws/driver/{vehicle_id}")
async def driver_ws(websocket: WebSocket, vehicle_id: int):
    await websocket.accept()
    driver_connections[vehicle_id] = websocket

    db = SessionLocal()
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle:
        vehicle.status = "active"
        db.commit()
    db.close()

    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)

            db = SessionLocal()
            v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
            if v:
                v.last_lat = parsed.get("lat")
                v.last_lng = parsed.get("lng")
                v.last_seen = datetime.utcnow()
                v.status = "active"
                db.commit()
            db.close()

            payload = json.dumps({
                "type": "location_update",
                "vehicle_id": vehicle_id,
                "lat": parsed.get("lat"),
                "lng": parsed.get("lng")
            })
            for conn in dashboard_connections[:]:
                try:
                    await conn.send_text(payload)
                except:
                    dashboard_connections.remove(conn)
    except WebSocketDisconnect:
        driver_connections.pop(vehicle_id, None)
        db = SessionLocal()
        v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if v:
            v.status = "idle"
            db.commit()
        db.close()


@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    await websocket.accept()
    dashboard_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in dashboard_connections:
            dashboard_connections.remove(websocket)


# ==================== Pages ====================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/driver", response_class=HTMLResponse)
def driver_page(request: Request):
    db = SessionLocal()
    vehicles = db.query(Vehicle).all()
    db.close()
    return templates.TemplateResponse("driver.html", {"request": request, "vehicles": vehicles})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()
    records = db.query(RouteHistory).order_by(RouteHistory.timestamp.desc()).all()
    vehicles = db.query(Vehicle).all()

    total_runs = len(records)
    total_fuel_saved = sum(r.fuel_saved for r in records)
    total_cost_saved = total_fuel_saved * FUEL_PRICE
    avg_distance_saved = sum((r.random_distance - r.optimized_distance) for r in records) / total_runs if total_runs > 0 else 0

    db.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "records": records,
        "vehicles": vehicles,
        "total_runs": total_runs,
        "total_fuel_saved": round(total_fuel_saved, 2),
        "total_cost_saved": round(total_cost_saved, 2),
        "avg_distance_saved": round(avg_distance_saved, 2)
    })


# ==================== Optimization API (Improved) ====================

@app.post("/optimize-route")
def optimize(data: LocationInput):
    delivery_points = [tuple(p) for p in data.locations if len(p) == 2]
    num_trucks = max(2, min(data.num_trucks, 5))   # between 2 to 5 trucks

    if len(delivery_points) < num_trucks:
        return {"error": f"At least {num_trucks} delivery points required for {num_trucks} trucks"}

    # Dynamically divide points among trucks
    chunk_size = math.ceil(len(delivery_points) / num_trucks)
    truck_results = []

    total_naive = 0
    total_optimized = 0
    total_fuel = 0
    total_cost = 0

    for i in range(num_trucks):
        start = i * chunk_size
        end = start + chunk_size
        points = delivery_points[start:end]

        if not points:
            continue

        all_points = [WAREHOUSE] + points
        naive_dist = calculate_distance(all_points)
        best_route, best_dist = genetic_algorithm(all_points)

        fuel_saved = max((naive_dist - best_dist) * FUEL_RATE, 0)
        cost_saved = fuel_saved * FUEL_PRICE
        eta = best_dist / AVERAGE_SPEED

        truck_results.append({
            "truck_id": i + 1,
            "route": best_route,
            "metrics": {
                "naive_distance": round(naive_dist, 2),
                "optimized_distance": round(best_dist, 2),
                "fuel_saved_litres": round(fuel_saved, 2),
                "cost_saved_inr": round(cost_saved, 2),
                "eta_hours": round(eta, 2)
            }
        })

        total_naive += naive_dist
        total_optimized += best_dist
        total_fuel += fuel_saved
        total_cost += cost_saved

    # Save to DB
    db = SessionLocal()
    db.add(RouteHistory(
        random_distance=round(total_naive, 2),
        optimized_distance=round(total_optimized, 2),
        fuel_saved=round(total_fuel, 2)
    ))
    db.commit()
    db.close()

    return {
        "warehouse": WAREHOUSE,
        "num_trucks": num_trucks,
        "total_cost_saved_inr": round(total_cost, 2),
        "total_eta_hours": round(max(t["metrics"]["eta_hours"] for t in truck_results), 2),
        "trucks": truck_results
    }