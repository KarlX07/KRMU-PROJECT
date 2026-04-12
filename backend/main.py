import sys
import os
import json
import requests
import random
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse   # ← RedirectResponse added
from fastapi.templating import Jinja2Templates

# ✅ FIX: Add the current 'backend' directory to sys.path 
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database import SessionLocal, Vehicle, RouteHistory, User, init_db      # ← User added
from ga_optimizer import genetic_algorithm, calculate_distance
from auth import (                                                             # ← NEW import
    verify_password, create_token, decode_token,
    get_current_user, TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Fleet Intelligence System")

template_path = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=template_path)

init_db()

dashboard_connections = []


# ─────────────────────────────────────────────────────────────────────────────
# ── NEW: AUTH HELPER ──
# ─────────────────────────────────────────────────────────────────────────────
def auth_guard(request: Request, role: str = "admin"):
    """Returns a RedirectResponse if user is not logged in / wrong role, else None."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url=f"/login?next={request.url.path}", status_code=302)
    if role == "admin" and user.get("role") != "admin":
        return RedirectResponse(url="/driver", status_code=302)
    if role == "driver" and user.get("role") not in ("driver", "admin"):
        return RedirectResponse(url="/login", status_code=302)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# ── NEW: LOGIN PAGE ──
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/login")
def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard" if user["role"] == "admin" else "/driver", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    data     = await request.json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role_req = data.get("role", "admin")

    db   = SessionLocal()
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    db.close()

    if not user or not verify_password(password, user.password_hash):
        return JSONResponse(status_code=401, content={"success": False, "detail": "Invalid username or password."})

    if role_req == "admin" and user.role != "admin":
        return JSONResponse(status_code=403, content={"success": False, "detail": "This account does not have admin access."})

    if role_req == "driver" and user.role not in ("driver", "admin"):
        return JSONResponse(status_code=403, content={"success": False, "detail": "This account does not have driver access."})

    token = create_token({"sub": user.username, "role": user.role, "full_name": user.full_name, "user_id": user.id},
                         expires_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES))

    response = JSONResponse(content={"success": True, "role": user.role})
    response.set_cookie(key="fleet_token", value=token, httponly=True,
                        max_age=TOKEN_EXPIRE_MINUTES * 60, samesite="lax", secure=False)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("fleet_token")
    return response


# ─────────────────────────────────────────────────────────────────────────────
# ── ORIGINAL ROUTES (unchanged logic, only auth guard added) ──
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/manifest.json")
def manifest():
    """Returns PWA manifest for the Driver App."""
    return {
        "name": "Fleet Driver App", 
        "short_name": "Driver", 
        "start_url": "/driver", 
        "display": "standalone", 
        "background_color": "#0f172a", 
        "theme_color": "#0f172a"
    }

def cluster_locations(locations, k):
    """Groups delivery points into clusters for 'k' number of trucks using KMeans."""
    if len(locations) <= k: return [[loc] for loc in locations]
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(locations)
    clusters = [[] for _ in range(k)]
    for i, label in enumerate(kmeans.labels_): 
        clusters[label].append(locations[i])
    return clusters

def get_route_geometry(route):
    """Fetches real road-network geometry from OSRM API for accurate map rendering."""
    try:
        coords = ";".join([f"{p[1]},{p[0]}" for p in route])
        url = f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson"
        res = requests.get(url, timeout=5)
        data = res.json()
        if "routes" in data: 
            return data["routes"][0]["geometry"]["coordinates"]
    except Exception as e:
        print(f"OSRM API Error: {e}")
    return [[p[1], p[0]] for p in route]


@app.get("/")
def home(request: Request):
    """Renders the main Route Optimizer page."""
    guard = auth_guard(request, role="admin")   # ← protected
    if guard: return guard
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/driver")
def driver_page(request: Request):
    """Renders the Driver tracking page with available vehicles."""
    guard = auth_guard(request, role="driver")  # ← protected
    if guard: return guard
    db = SessionLocal()
    vehicles = db.query(Vehicle).all()
    db.close()
    return templates.TemplateResponse("driver.html", {"request": request, "vehicles": vehicles})


@app.get("/dashboard")
def dashboard(request: Request):
    """Renders the Admin Dashboard with stats and optimization history."""
    guard = auth_guard(request, role="admin")   # ← protected
    if guard: return guard
    db = SessionLocal()
    vehicles = db.query(Vehicle).all()
    records_db = db.query(RouteHistory).order_by(RouteHistory.timestamp.desc()).all()
    records = []
    for r in records_db:
        records.append({
            "id": r.id,
            "random_distance": round(r.random_distance, 2),
            "optimized_distance": round(r.optimized_distance, 2),
            "fuel_saved": round(r.fuel_saved, 2),
            "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M") if r.timestamp else "-"
        })
    total_fuel = sum(r['fuel_saved'] for r in records) if records else 0
    db.close()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "vehicles": vehicles, 
        "records": records, 
        "total_runs": len(records), 
        "total_fuel_saved": round(total_fuel, 2), 
        "total_cost_saved": round(total_fuel * 95, 2),
        "avg_distance_saved": 0
    })


@app.post("/optimize-route")
async def optimize_route(data: dict):
    """Handles the route optimization request using Genetic Algorithm."""
    locations = data.get("locations", [])
    num_trucks = data.get("num_trucks", 2)
    trucks = []
    total_opt = 0
    total_base = 0
    chunks = cluster_locations(locations, num_trucks)
    db = SessionLocal()
    for i, chunk in enumerate(chunks):
        if len(chunk) < 2: continue
        route, opt = genetic_algorithm(chunk)
        base = opt * 1.3 
        total_opt += opt
        total_base += base
        trucks.append({
            "truck_id": i+1, 
            "route": route, 
            "geometry": get_route_geometry(route), 
            "metrics": {
                "optimized_distance": round(opt, 2), 
                "random_distance": round(base, 2), 
                "fuel_saved_litres": round((base-opt)/5, 2)
            }
        })
    fuel_saved = (total_base - total_opt) / 5.0
    db.add(RouteHistory(random_distance=total_base, optimized_distance=total_opt, fuel_saved=fuel_saved))
    db.commit()
    db.close()
    return {
        "warehouse": [28.6139, 77.2090], 
        "trucks": trucks, 
        "total_cost_saved_inr": round(fuel_saved * 95, 2), 
        "total_eta_hours": 2,
        "comparison": {
            "random_total": round(total_base, 2), 
            "optimized_total": round(total_opt, 2), 
            "improvement_percent": 20
        }
    }


@app.websocket("/ws/driver/{vehicle_id}")
async def driver_ws(websocket: WebSocket, vehicle_id: int):
    """WebSocket endpoint for receiving real-time GPS from drivers."""
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
                vehicle.status = "active"
                db.commit()
                for conn in dashboard_connections:
                    await conn.send_text(json.dumps({
                        "vehicle_id": vehicle_id, 
                        "lat": payload["lat"], 
                        "lng": payload["lng"]
                    }))
    except Exception:
        pass
    finally:
        db.close()


@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    """WebSocket endpoint to push live tracking data to the admin dashboard."""
    await websocket.accept()
    dashboard_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        dashboard_connections.remove(websocket)
