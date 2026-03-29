from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from backend.database import SessionLocal, Vehicle, RouteHistory, init_db
from backend.ga_optimizer import genetic_algorithm, calculate_distance
from datetime import datetime
import json
import requests
from sklearn.cluster import KMeans

app = FastAPI(title="Fleet Intelligence System")

templates = Jinja2Templates(directory="backend/templates")

init_db()

dashboard_connections = []

# -------------------- PWA MANIFEST --------------------

@app.get("/manifest.json")
def manifest():
    return {
        "name": "Fleet Driver App",
        "short_name": "Driver",
        "description": "Real-time fleet tracking and route optimization system",
        "start_url": "/driver",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0f172a",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/1995/1995520.png",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    }

# -------------------- CLUSTER --------------------

def cluster_locations(locations, k):
    if len(locations) < k:
        return [locations]

    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(locations)

    clusters = [[] for _ in range(k)]
    for i, label in enumerate(kmeans.labels_):
        clusters[label].append(locations[i])

    return clusters

# -------------------- ROUTE GEOMETRY --------------------

def get_route_geometry(route):
    try:
        coords = ";".join([f"{p[1]},{p[0]}" for p in route])
        url = f"https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"

        res = requests.get(url, timeout=5)
        data = res.json()

        if "routes" in data:
            return data["routes"][0]["geometry"]["coordinates"]

    except:
        pass

    return [[p[1], p[0]] for p in route]

# -------------------- BASELINE --------------------

def worst_case_distance(points):
    sorted_points = sorted(points, key=lambda x: (x[0], x[1]))
    return calculate_distance(sorted_points) * 1.4

# -------------------- ROUTES --------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 🔥 DRIVER ROUTE FIX (MAIN)
@app.get("/driver", response_class=HTMLResponse)
def driver_page(request: Request):
    db = SessionLocal()
    vehicles = db.query(Vehicle).all()
    db.close()

    html = templates.get_template("driver.html").render({
        "request": request,
        "vehicles": vehicles
    })

    return HTMLResponse(content=html)


# 🔥 EXTRA FIX FOR /driver/
@app.get("/driver/", response_class=HTMLResponse)
def driver_page_slash(request: Request):
    db = SessionLocal()
    vehicles = db.query(Vehicle).all()
    db.close()

    html = templates.get_template("driver.html").render({
        "request": request,
        "vehicles": vehicles
    })

    return HTMLResponse(content=html)


# 🔥 HEAD FIX (VERY IMPORTANT FOR PWA BUILDER)
@app.head("/driver")
def head_driver():
    return HTMLResponse(content="")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    db = SessionLocal()

    vehicles = db.query(Vehicle).all()
    records_db = db.query(RouteHistory).all()

    records = []
    for r in records_db:
        records.append({
            "id": r.id,
            "random_distance": r.random_distance,
            "optimized_distance": r.optimized_distance,
            "fuel_saved": r.fuel_saved
        })

    total_runs = len(records)
    total_fuel_saved = sum(r["fuel_saved"] for r in records) if records else 0
    total_cost_saved = round(total_fuel_saved * 90, 2)

    avg_distance_saved = round(
        sum((r["random_distance"] - r["optimized_distance"]) for r in records) / total_runs, 2
    ) if records else 0

    db.close()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "vehicles": vehicles,
        "records": records,
        "total_runs": total_runs,
        "total_fuel_saved": round(total_fuel_saved, 2),
        "total_cost_saved": total_cost_saved,
        "avg_distance_saved": avg_distance_saved
    })

# -------------------- OPTIMIZE --------------------

@app.post("/optimize-route")
async def optimize_route(data: dict):
    locations = data.get("locations", [])
    num_trucks = data.get("num_trucks", 2)

    if not locations or len(locations) < num_trucks:
        return JSONResponse({"error": "Invalid locations"})

    trucks = []
    total_distance = 0
    total_random_distance = 0

    chunks = cluster_locations(locations, num_trucks)
    chunks = [c for c in chunks if len(c) > 1]

    for i, chunk in enumerate(chunks):

        random_dist = worst_case_distance(chunk)
        route, dist = genetic_algorithm(chunk)

        total_distance += dist
        total_random_distance += random_dist

        geometry = get_route_geometry(route)

        improvement_percent = round(
            ((random_dist - dist) / random_dist) * 100 if random_dist else 0,
            2
        )

        trucks.append({
            "truck_id": i + 1,
            "route": route,
            "geometry": geometry,
            "metrics": {
                "optimized_distance": round(dist, 2),
                "random_distance": round(random_dist, 2),
                "improvement_percent": improvement_percent,
                "fuel_saved_litres": round(dist * 0.2, 2)
            }
        })

    improvement = (
        ((total_random_distance - total_distance) / total_random_distance) * 100
        if total_random_distance else 0
    )

    db = SessionLocal()
    db.add(RouteHistory(
        random_distance=round(total_random_distance, 2),
        optimized_distance=round(total_distance, 2),
        fuel_saved=round(total_distance * 0.2, 2)
    ))
    db.commit()
    db.close()

    return {
        "warehouse": [28.6139, 77.2090],
        "trucks": trucks,
        "total_cost_saved_inr": round(total_distance * 0.2 * 90, 2),
        "total_eta_hours": round(total_distance / 40, 2),
        "comparison": {
            "random_total": round(total_random_distance, 2),
            "optimized_total": round(total_distance, 2),
            "improvement_percent": round(improvement, 2)
        }
    }

# -------------------- WEBSOCKET --------------------

@app.websocket("/ws/driver/{vehicle_id}")
async def driver_ws(websocket: WebSocket, vehicle_id: int):
    await websocket.accept()
    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)

            vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

            if vehicle:
                vehicle.last_lat = payload["lat"]
                vehicle.last_lng = payload["lng"]
                vehicle.last_seen = datetime.utcnow()
                vehicle.status = "active"
                db.commit()

                for conn in dashboard_connections:
                    await conn.send_text(json.dumps({
                        "vehicle_id": vehicle_id,
                        "lat": payload["lat"],
                        "lng": payload["lng"]
                    }))

    except WebSocketDisconnect:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle:
            vehicle.status = "idle"
            db.commit()
    finally:
        db.close()

@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    await websocket.accept()
    dashboard_connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        dashboard_connections.remove(websocket)

print("✅ FINAL VERSION (PWA FIX COMPLETE)")