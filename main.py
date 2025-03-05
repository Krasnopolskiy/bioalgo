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
        generations=20,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.01,
        elite_size=10,
        precision=15,
    )

    ga = GeneticAlgorithm(fitness_function=function, config=config)

    logger.info("Running genetic algorithm optimization...")
    ga_x, ga_f = ga.run()
    logger.info("Genetic solution found: f(%.6f) = %.6f", ga_x, ga_f)

    history = ga.get_history()
    animate(config, history)


def animate(config, history):
    output_file = os.path.join(OUTPUT_DIR, "genetic_animation.mp4")
    logger.info("Creating animation...")
    animate_population(
        generations_data=history["populations"],
        fitness_function=function,
        bounds=config.bounds,
        title="Genetic Algorithm Animation - %d Generations" % config.generations,
        output_file=output_file,
    )
    logger.info("Animation saved to %s", output_file)


if __name__ == "__main__":
    main()
