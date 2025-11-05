import csv
import random

# ======================================
# 1. READ CSV FILE
# ======================================
def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:] if x.strip() != '']
            program_ratings[program] = ratings
    return program_ratings

# ======================================
# 2. FITNESS FUNCTION
# ======================================
def fitness_function(schedule, ratings):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        if program in ratings and time_slot < len(ratings[program]):
            total_rating += ratings[program][time_slot]
    return total_rating

# ======================================
# 3. GENETIC ALGORITHM
# ======================================
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

def mutate(schedule, all_programs):
    mutation_point = random.randint(0, len(schedule) - 1)
    schedule[mutation_point] = random.choice(all_programs)
    return schedule

def genetic_algorithm(ratings, generations=100, population_size=50, crossover_rate=0.8, mutation_rate=0.2, elitism_size=2):
    all_programs = list(ratings.keys())
    time_slots = range(6, 24)

    population = []
    for _ in range(population_size):
        schedule = random.sample(all_programs, min(len(all_programs), len(time_slots)))
        population.append(schedule)

    for generation in range(generations):
        population.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
        new_population = population[:elitism_size]

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1, all_programs)
            if random.random() < mutation_rate:
                child2 = mutate(child2, all_programs)

            new_population.extend([child1, child2])

        population = new_population[:population_size]

    best = max(population, key=lambda s: fitness_function(s, ratings))
    return best
