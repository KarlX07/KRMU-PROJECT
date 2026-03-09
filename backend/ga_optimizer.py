import random
import math

# Calculate total route distance
def calculate_distance(route):
    total = 0
    for i in range(len(route)):
        x1, y1 = route[i]
        x2, y2 = route[(i + 1) % len(route)]
        total += math.dist((x1, y1), (x2, y2))
    return total

# Generate random route
def generate_random_route(locations):
    route = locations[:]
    random.shuffle(route)
    return route

# Create initial population
def create_population(locations, size):
    return [generate_random_route(locations) for _ in range(size)]

# Selection (keep best half)
def selection(population):
    population.sort(key=lambda route: calculate_distance(route))
    return population[:len(population)//2]

# Crossover (Ordered Crossover)
def crossover(parent1, parent2):
    start, end = sorted(random.sample(range(len(parent1)), 2))
    child = [None] * len(parent1)

    # Copy part from parent1
    child[start:end] = parent1[start:end]

    # Fill remaining from parent2
    pointer = 0
    for city in parent2:
        if city not in child:
            while child[pointer] is not None:
                pointer += 1
            child[pointer] = city

    return child

# Mutation (swap two cities randomly)
def mutate(route, mutation_rate=0.1):
    for i in range(len(route)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route

# Full Genetic Algorithm
def genetic_algorithm(locations, generations=200, population_size=10):
    population = create_population(locations, population_size)

    for _ in range(generations):
        population = selection(population)
        new_population = population[:]

        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)

        population = new_population

    best_route = min(population, key=lambda route: calculate_distance(route))
    return best_route, calculate_distance(best_route)