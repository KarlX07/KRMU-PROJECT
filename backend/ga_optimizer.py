import random
import math

# Haversine formula - real-world distance in km
def haversine(point1, point2):
    R = 6371
    lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def calculate_distance(route):
    total = 0
    for i in range(len(route)):
        total += haversine(route[i], route[(i + 1) % len(route)])
    return total

def create_population(locations, size=50):
    return [random.sample(locations, len(locations)) for _ in range(size)]

def selection(population, elite_size=5):
    population.sort(key=lambda route: calculate_distance(route))
    return population[:elite_size] + random.sample(population[elite_size:], len(population)//2 - elite_size)

def crossover(parent1, parent2):
    start, end = sorted(random.sample(range(len(parent1)), 2))
    child = [None] * len(parent1)
    child[start:end] = parent1[start:end]

    pointer = 0
    for city in parent2:
        if city not in child:
            while child[pointer] is not None:
                pointer += 1
            child[pointer] = city
    return child

def mutate(route, mutation_rate=0.15):
    for i in range(len(route)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(route)-1)
            route[i], route[j] = route[j], route[i]
    return route

def genetic_algorithm(locations, generations=300, population_size=80):
    if len(locations) < 2:
        return locations, 0

    population = create_population(locations, population_size)

    for gen in range(generations):
        elites = selection(population)
        new_population = elites[:]

        while len(new_population) < population_size:
            parent1, parent2 = random.sample(elites, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)

        population = new_population

    best_route = min(population, key=calculate_distance)
    return best_route, calculate_distance(best_route)