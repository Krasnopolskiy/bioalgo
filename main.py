import logging
import os

import numpy as np

from lib.config import Config
from lib.genetic import GeneticAlgorithm
from lib.visualization import animate_population

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

OUTPUT_DIR = "animations"


def function(x: float) -> float:
    return np.cos(3 * x - 15) * x


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    config = Config(
        bounds=(-9.6, 9.1),
        population_size=1000,
        generations=100,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elite_size=100,
    )
    ga = GeneticAlgorithm(
        fitness_function=function,
        config=config,
    )

    best_solution, best_fitness = ga.run()

    logger.info("Best solution found: x = %.6f", best_solution)
    logger.info("Function value at best solution: f(x) = %.6f", best_fitness)

    # Get history data including populations
    history = ga.get_history()

    # Create animation
    output_file = os.path.join(OUTPUT_DIR, "genetic_animation.mp4")
    logger.info("Creating animation...")
    animate_population(
        generations_data=history["populations"],
        fitness_function=function,
        bounds=config.bounds,
        title=f"Genetic Algorithm Animation - {config.generations} Generations",
        output_file=output_file,
    )
    logger.info(f"Animation saved to {output_file}")


if __name__ == "__main__":
    main()
