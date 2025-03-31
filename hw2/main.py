import logging
import os
import time
import itertools

import numpy as np

from lib.config import Config
from lib.genetic import GeneticAlgorithm
from lib.visualization import animate_tsp

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

OUTPUT_DIR = "animations"


def calculate_distance(tour: np.ndarray) -> float:
    total_distance = 0
    cities = config.cities

    for i in range(len(tour)):
        from_city = tour[i]
        to_city = tour[(i + 1) % len(tour)]
        distance = np.linalg.norm(cities[from_city] - cities[to_city])
        total_distance += distance

    return total_distance


def solve_tsp_brute_force(cities):
    num_cities = len(cities)

    best_distance = float("inf")
    best_tour = None

    start_time = time.time()

    all_tours = list(itertools.permutations(range(num_cities)))
    logger.info("Всего возможных маршрутов: %d", len(all_tours))

    for tour in all_tours:
        tour = np.array(tour)
        distance = calculate_distance(tour)
        if distance < best_distance:
            best_distance = distance
            best_tour = tour

    end_time = time.time()

    logger.info("Брутфорс решение: %.2f (занято времени: %.2f сек)", best_distance, end_time - start_time)
    return best_tour, best_distance


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    num_cities = 10
    cities = np.random.rand(num_cities, 2) * 100

    global config
    config = Config(
        cities=cities,
        population_size=100,
        generations=50,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elite_size=5,
    )

    start_time = time.time()
    logger.info("Запуск генетического алгоритма для задачи коммивояжера...")
    ga = GeneticAlgorithm(fitness_function=calculate_distance, config=config)
    best_tour_ga, best_distance_ga = ga.run()
    end_time = time.time()
    logger.info("GA: Найден маршрут с длиной: %.2f (занято времени: %.2f сек)", best_distance_ga, end_time - start_time)

    logger.info("Запуск брутфорс метода для сравнения...")
    best_tour_bf, best_distance_bf = solve_tsp_brute_force(config.cities)

    logger.info("Сравнение результатов:")
    logger.info("Брутфорс метод: %.2f", best_distance_bf)
    logger.info("Генетический алгоритм: %.2f", best_distance_ga)
    logger.info("Разница: %.2f%%", 100 * (best_distance_ga - best_distance_bf) / best_distance_bf)

    history = ga.get_history()
    animate(config, history)


def animate(config, history):
    output_file = os.path.join(OUTPUT_DIR, "tsp_animation.mp4")
    logger.info("Создание анимации...")
    animate_tsp(
        generations_data=history["populations"],
        fitness_data=history["fitness"],
        cities=config.cities,
        title="Генетический алгоритм для TSP - %d поколений" % config.generations,
        output_file=output_file,
    )
    logger.info("Анимация сохранена в %s", output_file)


if __name__ == "__main__":
    main()
