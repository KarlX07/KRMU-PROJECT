from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./fleet.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_name = Column(String, nullable=False)
    driver_name = Column(String)
    fuel_type = Column(String, default="Diesel")
    status = Column(String, default="idle")
    last_lat = Column(Float, nullable=True)
    last_lng = Column(Float, nullable=True)
    last_seen = Column(DateTime, nullable=True)

class RouteHistory(Base):
    __tablename__ = "route_history"
    id = Column(Integer, primary_key=True, index=True)
    random_distance = Column(Float)
    optimized_distance = Column(Float)
    fuel_saved = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ── NEW: User model for login ──────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role          = Column(String, nullable=False)   # "admin" | "driver"
    full_name     = Column(String, nullable=True)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
# ──────────────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Original vehicle seeding — unchanged
    if db.query(Vehicle).count() == 0:
        db.add_all([
            Vehicle(vehicle_name="Truck 1", driver_name="Ramesh Kumar"),
            Vehicle(vehicle_name="Truck 2", driver_name="Suresh Singh"),
        ])
        db.commit()

    # ── NEW: Seed default users ──
    if db.query(User).count() == 0:
        from auth import hash_password
        db.add_all([
            User(username="admin",   password_hash=hash_password("admin123"),  role="admin",  full_name="Super Admin"),
            User(username="driver1", password_hash=hash_password("driver123"), role="driver", full_name="Ramesh Kumar"),
            User(username="driver2", password_hash=hash_password("driver456"), role="driver", full_name="Suresh Singh"),
        ])
        db.commit()
    # ────────────────────────────

    db.close()
