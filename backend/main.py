from fastapi import FastAPI
from pydantic import BaseModel
from backend.ga_optimizer import genetic_algorithm, calculate_distance, generate_random_route

app = FastAPI()

class LocationInput(BaseModel):
    locations: list

@app.get("/")
def home():
    return {"message": "Fleet Management Backend Running"}

@app.post("/optimize-route")
def optimize(data: LocationInput):
    locations = data.locations

    # Random route (comparison ke liye)
    random_route = generate_random_route(locations)
    random_distance = calculate_distance(random_route)

    # Genetic Algorithm run
    best_route, best_distance = genetic_algorithm(locations)

    # Fuel simulation (assume kar rahe hain)
    fuel_rate = 0.2  # liters per unit distance

    random_fuel = random_distance * fuel_rate
    optimized_fuel = best_distance * fuel_rate

    return {
        "metrics": {
            "random_distance": random_distance,
            "optimized_distance": best_distance,
            "distance_saved": random_distance - best_distance,
            "random_fuel_consumed": random_fuel,
            "optimized_fuel_consumed": optimized_fuel,
            "fuel_saved": random_fuel - optimized_fuel
        },
        "optimized_route": best_route
    }
