import ast
import csv
import fcntl
import logging
import multiprocessing
import random
import time
from pathlib import Path

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = Path("data")
NUM_PROCESSES = 15
POPULATION_SIZE = 200
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.8
TOURNAMENT_SIZE = 5
MAX_GENERATIONS = 1000
MAX_TIME_SECONDS = 300

# Table of variants
VARIANTS = [
    {"number": 1, "n": 24, "divider": 0.8, "modulo": False},
    {"number": 2, "n": 24, "divider": 1.0, "modulo": False},
    {"number": 3, "n": 24, "divider": 1.2, "modulo": False},
    {"number": 4, "n": 24, "divider": 1.4, "modulo": False},
    {"number": 5, "n": 24, "divider": 0.8, "modulo": True},
    {"number": 6, "n": 24, "divider": 1.0, "modulo": True},
    {"number": 7, "n": 24, "divider": 1.2, "modulo": True},
    {"number": 8, "n": 24, "divider": 1.4, "modulo": True},
]


def load_problems(path: Path) -> list:
    problems = []
    with open(path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for i, row in enumerate(reader, 1):
            problem_idx = int(row[0])
            vector_idx = int(row[1])
            target = int(row[2])
            ratio = float(row[3])
            problems.append((problem_idx, vector_idx, target, ratio))
    return problems


def load_vectors(path: Path) -> dict:
    vectors = {}
    with open(path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            vector_idx = int(row[0])
            vector = ast.literal_eval(row[1])
            vectors[vector_idx] = vector
    return vectors


def load_existing_results(path: Path) -> set:
    if not path.exists():
        with open(path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(
                [
                    "Номер задачи",
                    "Время работы алгортима",
                    "Достигнутый минимум фитнесс-функции",
                    "Причина остановки алгоритма",
                    "Номер последнего поколения",
                ]
            )
        return set()

    solved_problems = set()
    with open(path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            if row:
                solved_problems.add(int(row[0]))
    return solved_problems


def fitness_function(chromosome: list, vector: list, target: int, use_modulo: bool) -> int:
    if use_modulo:
        a_max = max(vector)
        modulo = a_max + 1
        total_weight = sum(v * c for v, c in zip(vector, chromosome)) % modulo
        return abs((target % modulo) - total_weight)
    else:
        total_weight = sum(v * c for v, c in zip(vector, chromosome))
        return abs(target - total_weight)


def create_individual(length: int) -> list:
    return [random.randint(0, 1) for _ in range(length)]


def initialize_population(pop_size: int, chromosome_length: int) -> list:
    return [create_individual(chromosome_length) for _ in range(pop_size)]


def tournament_selection(population: list, fitnesses: list, tournament_size: int) -> list:
    selected = random.sample(range(len(population)), tournament_size)
    best_idx = min(selected, key=lambda i: fitnesses[i])
    return population[best_idx]


def crossover(parent1: list, parent2: list, rate: float) -> tuple:
    if random.random() > rate:
        return parent1, parent2

    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def mutate(chromosome: list, rate: float) -> list:
    mutated = chromosome.copy()
    for i in range(len(mutated)):
        if random.random() < rate:
            mutated[i] = 1 - mutated[i]
    return mutated


def evolve_population(population: list, fitnesses: list) -> list:
    new_population = []
    for _ in range(POPULATION_SIZE // 2):
        parent1 = tournament_selection(population, fitnesses, TOURNAMENT_SIZE)
        parent2 = tournament_selection(population, fitnesses, TOURNAMENT_SIZE)

        child1, child2 = crossover(parent1, parent2, CROSSOVER_RATE)

        child1 = mutate(child1, MUTATION_RATE)
        child2 = mutate(child2, MUTATION_RATE)

        new_population.extend([child1, child2])
    return new_population


def estimate_max_time(vector: list, target: int) -> float:
    n = len(vector)
    max_weight = max(vector)
    complexity = n * max_weight * np.log(target + 1)
    return min(MAX_TIME_SECONDS, complexity / 10000)


def genetic_algorithm(vector: list, target: int, use_modulo: bool) -> tuple:
    start_time = time.time()
    n = len(vector)
    population = initialize_population(POPULATION_SIZE, n)
    max_time_limit = estimate_max_time(vector, target)

    generation = 0
    best_fitness_history = []
    best_chromosome = None

    while generation < MAX_GENERATIONS:
        fitnesses = [fitness_function(ind, vector, target, use_modulo) for ind in population]
        min_fitness = min(fitnesses)
        min_idx = fitnesses.index(min_fitness)

        best_chromosome = population[min_idx]
        best_fitness_history.append(min_fitness)

        if min_fitness == 0:
            stop_reason = "Найдено точное решение"
            break

        min_generations = int(MAX_GENERATIONS * 0.5)
        if generation >= min_generations and generation > 0 and best_fitness_history[-1] == best_fitness_history[-2]:
            stop_reason = "Нет улучшений на последних двух итерациях"
            break

        if time.time() - start_time > max_time_limit:
            stop_reason = "Превышено время работы"
            break

        population = evolve_population(population, fitnesses)
        generation += 1

    else:
        stop_reason = "Достигнуто максимальное число поколений"

    total_time = time.time() - start_time
    min_fitness = fitness_function(best_chromosome, vector, target, use_modulo)

    return total_time, min_fitness, stop_reason, generation


def save_result_to_file(result: tuple, path: Path) -> None:
    problem_idx, time_used, min_fitness, stop_reason, last_gen = result
    with open(path, "a", newline="") as csvfile:
        fcntl.flock(csvfile, fcntl.LOCK_EX)
        try:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow([problem_idx, "%.6f" % time_used, min_fitness, stop_reason, last_gen])
        finally:
            fcntl.flock(csvfile, fcntl.LOCK_UN)


def solve_single_problem(args: tuple) -> tuple:
    problem_idx, vector_idx, target, ratio, vector, use_modulo, results_path = args
    time_used, min_fitness, stop_reason, generation = genetic_algorithm(vector, target, use_modulo)

    result = (problem_idx, time_used, min_fitness, stop_reason, generation)
    save_result_to_file(result, results_path)
    logging.info(
        "Solved problem %d with GA: min_fitness=%d, time=%.4f seconds, stop=%s",
        problem_idx,
        min_fitness,
        time_used,
        stop_reason,
    )
    return result


def solve_all_problems_parallel(
    problems: list, vectors: dict, solved_problems: set, use_modulo: bool, results_path: Path
) -> None:
    unsolved_problems = [p for p in problems if p[0] not in solved_problems]
    if not unsolved_problems:
        logging.info("All problems already solved")
        return

    problem_args = [(p[0], p[1], p[2], p[3], vectors[p[1]], use_modulo, results_path) for p in unsolved_problems]
    logging.info("Starting %d processes for %d unsolved problems", NUM_PROCESSES, len(problem_args))

    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        pool.map(solve_single_problem, problem_args)


def solve_for_variant(variant_num: int) -> None:
    variant = next((v for v in VARIANTS if v["number"] == variant_num), None)
    if not variant:
        logging.error(f"Invalid variant number: {variant_num}")
        return

    option_dir = BASE_DIR / f"option{variant_num}"

    vectors_path = option_dir / "knapsack_vectors.csv"
    problems_path = option_dir / "knapsack_problems.csv"
    results_path = option_dir / "genetic_results.csv"

    use_modulo = variant["modulo"]

    vectors = load_vectors(vectors_path)
    logging.info("Loaded %d knapsack vectors for variant %d", len(vectors), variant_num)

    problems = load_problems(problems_path)
    logging.info("Loaded %d knapsack problems for variant %d", len(problems), variant_num)

    solved_problems = load_existing_results(results_path)
    logging.info("Found %d already solved problems with GA for variant %d", len(solved_problems), variant_num)

    solve_all_problems_parallel(problems, vectors, solved_problems, use_modulo, results_path)
    logging.info("Completed genetic algorithm solutions for variant %d", variant_num)


def main() -> None:
    if multiprocessing.get_start_method() != "spawn":
        multiprocessing.set_start_method("spawn", force=True)

    for variant in range(8):
        solve_for_variant(variant + 1)


if __name__ == "__main__":
    main()
