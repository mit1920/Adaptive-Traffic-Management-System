import numpy as np

# Fitness function to evaluate delay and penalty based on vehicle counts and green times
def fitness_function(C, g, x, c, vehicles, green_times):
    # Calculate delay and penalty terms
    a = (1 - (g / C)) ** 2
    p = 1 - ((g / C) * x)
    d1i = (0.38 * C * a) / p

    a2 = 173 * (x ** 2)
    ri1 = np.sqrt((x - 1) + (x - 1) ** 2 + ((16 * x) / c))
    d2i = a2 * ri1

    # Adding a penalty if the green time is not proportional to vehicle count
    vehicle_proportion = np.array(vehicles) / sum(vehicles)
    green_proportion = np.array(green_times) / sum(green_times)  # Corrected line for proportionality

    penalty_factor = np.sum(np.abs(green_proportion - vehicle_proportion) * 100)  # Adjust the factor as necessary
    return d1i + d2i + penalty_factor

# Normalize the green times based on vehicle count proportion
def normalize_green_times(green_times, vehicles, cycle_time):
    total_vehicles = sum(vehicles)
    if total_vehicles == 0:
        return green_times  # Avoid division by zero
    vehicle_proportion = [v / total_vehicles for v in vehicles]
    
    # Calculate green times based on proportion
    normalized_times = [int(cycle_time * p) for p in vehicle_proportion]

    # Check if the sum of normalized green times exceeds the cycle time
    total_normalized = sum(normalized_times)
    if total_normalized > cycle_time:
        normalized_times = [int(t * cycle_time / total_normalized) for t in normalized_times]

    return normalized_times

# Initialize population for genetic algorithm
def initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, cars):
    population = []
    road_capacity = [20] * num_lights
    road_congestion = np.array(road_capacity) - np.array(cars)
    road_congestion = road_congestion / np.array(road_capacity)

    while len(population) < pop_size:
        green_times = np.random.randint(green_min, green_max + 1, num_lights)
        if np.sum(green_times) <= cycle_time:
            # Normalize green times based on vehicle count
            normalized_times = normalize_green_times(green_times, cars, cycle_time)

            # Calculate the total delay for this individual (based on the fitness function)
            total_delay = np.sum([fitness_function(cycle_time, normalized_times[i], road_congestion[i], road_capacity[i], cars, normalized_times) for i in range(num_lights)])
            population.append((normalized_times, total_delay))

    return sorted(population, key=lambda x: x[1])  # Sort by total delay, the best ones are at the top

# Roulette wheel selection method to select parents
def roulette_wheel_selection(population, total_delays, beta):
    worst_delay = max(total_delays)
    probabilities = np.exp(-beta * np.array(total_delays) / worst_delay)
    probabilities /= np.sum(probabilities)
    return np.random.choice(len(population), p=probabilities)

# Crossover function to create two offspring from two parents
def crossover(parent1, parent2, num_lights):
    point = np.random.randint(1, num_lights)
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])
    return child1, child2

# Mutation function to mutate an individual
def mutate(individual, mutation_rate, green_min, green_max):
    num_lights = len(individual)
    mutated = individual.copy()
    for _ in range(int(mutation_rate * num_lights)):
        idx = np.random.randint(0, num_lights)
        sigma = np.random.choice([-1, 1]) * 0.02 * (green_max - green_min)
        mutated[idx] = np.clip(individual[idx] + sigma, green_min, green_max)
    return mutated

# Inversion function to reverse a section of the individual's green times
def inversion(individual, num_lights):
    idx1, idx2 = np.random.randint(0, num_lights, 2)
    if idx1 > idx2:
        idx1, idx2 = idx2, idx1
    individual[idx1:idx2+1] = individual[idx1:idx2+1][::-1]
    return individual

# Main genetic algorithm to optimize the traffic signal timings
def genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, cycle_time, mutation_rate, pinv, beta, cars):
    population = initialize_population(pop_size, num_lights, green_min, green_max, cycle_time, cars)
    best_sol = population[0]
    best_delays = [best_sol[1]]

    road_capacity = [20] * num_lights
    road_congestion = np.array(road_capacity) - np.array(cars)
    road_congestion = road_congestion / np.array(road_capacity)

    for _ in range(max_iter):
        total_delays = [ind[1] for ind in population]
        new_population = []

        while len(new_population) < pop_size:
            i1 = roulette_wheel_selection(population, total_delays, beta)
            i2 = roulette_wheel_selection(population, total_delays, beta)

            parent1, parent2 = population[i1][0], population[i2][0]
            child1, child2 = crossover(parent1, parent2, num_lights)

            # Check if child1 green time is valid and mutate
            if np.sum(child1) <= cycle_time:
                child1 = mutate(child1, mutation_rate, green_min, green_max)
                child1 = np.clip(child1, green_min, green_max)
                total_delay = np.sum([fitness_function(cycle_time, child1[i], road_congestion[i], road_capacity[i], cars, child1) for i in range(num_lights)])
                new_population.append((child1, total_delay))

            # Check if child2 green time is valid and mutate
            if np.sum(child2) <= cycle_time:
                child2 = mutate(child2, mutation_rate, green_min, green_max)
                child2 = np.clip(child2, green_min, green_max)
                total_delay = np.sum([fitness_function(cycle_time, child2[i], road_congestion[i], road_capacity[i], cars, child2) for i in range(num_lights)])
                new_population.append((child2, total_delay))

        # Apply inversion and ensure green times are valid
        while len(new_population) < pop_size:
            i = np.random.randint(0, len(population))
            individual = inversion(population[i][0], num_lights)
            if np.sum(individual) <= cycle_time:
                individual = mutate(individual, mutation_rate, green_min, green_max)
                total_delay = np.sum([fitness_function(cycle_time, individual[i], road_congestion[i], road_capacity[i], cars, individual) for i in range(num_lights)])
                new_population.append((individual, total_delay))

        # Merge and select the best population
        population += new_population
        population = sorted(population, key=lambda x: x[1])[:pop_size]
        
        if population[0][1] < best_sol[1]:
            best_sol = population[0]
        
        best_delays.append(best_sol[1])
        print(f"Iteration: Best Total Delay = {best_sol[1]}")
        print(f"Green Times: North = {best_sol[0][0]}, South = {best_sol[0][1]}, West = {best_sol[0][2]}, East = {best_sol[0][3]}")
    
    return best_sol, best_delays

# Main function to optimize the traffic signal timings
def optimize_traffic(cars):
    # Default parameters
    pop_size = 400
    num_lights = 4
    max_iter = 25
    green_min = 10
    green_max = 60
    cycle_time = 160 - 12
    mutation_rate = 0.02
    pinv = 0.2
    beta = 8

    # Run Genetic Algorithm with default parameters
    best_sol, best_delays = genetic_algorithm(pop_size, num_lights, max_iter, green_min, green_max, cycle_time, mutation_rate, pinv, beta, cars)

    # Convert numpy types to standard Python types
    result = {
        'north': int(best_sol[0][0]),
        'south': int(best_sol[0][1]),
        'west': int(best_sol[0][2]),
        'east': int(best_sol[0][3])
    }

    print('Optimal Solution:')
    print(f'North Green Time = {result["north"]} seconds')
    print(f'South Green Time = {result["south"]} seconds')
    print(f'West Green Time = {result["west"]} seconds')
    print(f'East Green Time = {result["east"]} seconds')

    return result