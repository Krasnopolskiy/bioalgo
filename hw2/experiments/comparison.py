import itertools
import logging
import os
import time

import matplotlib.pyplot as plt
import numpy as np
from lib.config import Config
from lib.genetic import GeneticAlgorithm

logger = logging.getLogger(__name__)


def calculate_distance(tour: np.ndarray, cities: np.ndarray) -> float:
    total_distance = 0

    for i in range(len(tour)):
        from_city = tour[i]
        to_city = tour[(i + 1) % len(tour)]
        distance = np.linalg.norm(cities[from_city] - cities[to_city])
        total_distance += distance

    return total_distance


def solve_tsp_brute_force(cities: np.ndarray) -> tuple[float, float]:
    num_cities = len(cities)

    start_time = time.time()

    best_distance = float("inf")
    all_tours = list(itertools.permutations(range(num_cities)))

    for tour in all_tours:
        tour = np.array(tour)
        distance = calculate_distance(tour, cities)
        if distance < best_distance:
            best_distance = distance

    end_time = time.time()
    execution_time = end_time - start_time

    return best_distance, execution_time


def solve_tsp_genetic(cities: np.ndarray, generations: int, population_size: int) -> tuple[float, float]:
    def fitness_func(tour: np.ndarray) -> float:
        return calculate_distance(tour, cities)

    config = Config(
        cities=cities,
        population_size=population_size,
        generations=generations,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elite_size=5,
    )

    ga = GeneticAlgorithm(fitness_function=fitness_func, config=config)

    start_time = time.time()
    best_tour, best_distance = ga.run()
    end_time = time.time()

    execution_time = end_time - start_time

    return best_distance, execution_time


def run_test(output_dir: str = "results", num_runs: int = 5) -> str:
    os.makedirs(output_dir, exist_ok=True)

    city_counts = range(3, 11)
    bf_times = []
    ga_times = []
    bf_distances = []
    ga_distances = []

    np.random.seed(42)

    for n in city_counts:
        logger.info(f"Testing with {n} cities...")

        bf_time_sum = 0
        ga_time_sum = 0
        bf_distance_sum = 0
        ga_distance_sum = 0

        for run in range(num_runs):
            cities = np.random.rand(n, 2) * 100

            bf_distance, bf_time = solve_tsp_brute_force(cities)
            bf_time_sum += bf_time
            bf_distance_sum += bf_distance

            # Для генетического алгоритма используем параметры, которые дадут хорошее решение
            # Увеличиваем количество поколений и размер популяции для более сложных задач
            population_size = max(50, n * 10)
            generations = max(20, n * 5)

            ga_distance, ga_time = solve_tsp_genetic(cities, generations, population_size)
            ga_time_sum += ga_time
            ga_distance_sum += ga_distance

            logger.info(f"Run {run + 1}/{num_runs} - BF time: {bf_time:.4f}s, GA time: {ga_time:.4f}s")
            logger.info(f"BF distance: {bf_distance:.2f}, GA distance: {ga_distance:.2f}")

        bf_times.append(bf_time_sum / num_runs)
        ga_times.append(ga_time_sum / num_runs)
        bf_distances.append(bf_distance_sum / num_runs)
        ga_distances.append(ga_distance_sum / num_runs)

        logger.info(f"Average for {n} cities - BF time: {bf_times[-1]:.4f}s, GA time: {ga_times[-1]:.4f}s")

    # Создаем график времени выполнения
    plt.figure(figsize=(10, 6))
    plt.plot(list(city_counts), bf_times, marker="o", label="Brute Force")
    plt.plot(list(city_counts), ga_times, marker="s", label="Genetic Algorithm")
    plt.xlabel("Number of Cities")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Execution Time Comparison: Brute Force vs Genetic Algorithm")
    plt.legend()
    plt.grid(True)

    time_output_file = os.path.join(output_dir, "bf_vs_ga_time.png")
    plt.savefig(time_output_file)
    plt.close()

    # Создаем график качества решения
    plt.figure(figsize=(10, 6))

    # Нормализуем расстояния относительно брутфорса (который является точным решением)
    relative_distances = [ga / bf * 100 - 100 for ga, bf in zip(ga_distances, bf_distances)]

    plt.bar(list(city_counts), relative_distances)
    plt.xlabel("Number of Cities")
    plt.ylabel("GA Solution Gap (%)")
    plt.title("GA Solution Quality Gap Compared to Optimal Solution")
    plt.grid(True, axis="y")

    quality_output_file = os.path.join(output_dir, "bf_vs_ga_quality.png")
    plt.savefig(quality_output_file)
    plt.close()

    return time_output_file


if __name__ == "__main__":
    from run_all_experiments import run_all_experiments

    run_all_experiments()
