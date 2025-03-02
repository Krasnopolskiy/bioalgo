import logging

import numpy as np

from lib.genetic import GeneticAlgorithm

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

BOUNDS = (-9.6, 9.1)
ELITE_SIZE = 5
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.8
GENERATIONS = 100
POPULATION_SIZE = 100


def function(x: float) -> float:
    return np.cos(3 * x - 15) * x


def main():
    ga = GeneticAlgorithm(
        fitness_function=function,
        bounds=BOUNDS,
        population_size=POPULATION_SIZE,
        generations=GENERATIONS,
        crossover_rate=CROSSOVER_RATE,
        mutation_rate=MUTATION_RATE,
        elite_size=ELITE_SIZE,
    )

    best_solution, best_fitness = ga.run()

    logger.info("Best solution found: x = %.6f", best_solution)
    logger.info("Function value at best solution: f(x) = %.6f", best_fitness)


if __name__ == "__main__":
    main()
