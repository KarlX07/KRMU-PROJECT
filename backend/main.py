from fastapi import FastAPI
from pydantic import BaseModel
from ga_optimizer import genetic_algorithm

app = FastAPI()

class LocationInput(BaseModel):
    locations: list

@app.get("/")
def home():
    return {"message": "Fleet Management Backend Running"}

@app.post("/optimize-route")
def optimize(data: LocationInput):
    best_route, best_distance = genetic_algorithm(data.locations)
    return {
        "optimized_route": best_route,
        "optimized_distance": best_distance
    }