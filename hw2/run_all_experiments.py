import logging
import os

import numpy as np
from experiments import crossover_rate, mutation_rate, population_size, population_time
from lib.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

OUTPUT_DIR = "results"


def run_all_experiments(output_dir=OUTPUT_DIR, num_runs=3):
    os.makedirs(output_dir, exist_ok=True)

    num_cities = 10
    np.random.seed(42)
    cities = np.random.rand(num_cities, 2) * 100

    base_config = Config(
        cities=cities,
        population_size=100,
        generations=30,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elite_size=5,
    )

    logger.info("Running crossover rate experiment...")
    crossover_output = crossover_rate.run_test(base_config, output_dir, num_runs)
    logger.info("Output saved to %s", crossover_output)

    logger.info("Running mutation rate experiment...")
    mutation_output = mutation_rate.run_test(base_config, output_dir, num_runs)
    logger.info("Output saved to %s", mutation_output)

    logger.info("Running population size experiment...")
    pop_size_output = population_size.run_test(base_config, output_dir, num_runs)
    logger.info("Output saved to %s", pop_size_output)

    logger.info("Running population time experiment...")
    pop_time_output = population_time.run_test(base_config, output_dir, num_runs)
    logger.info("Output saved to %s", pop_time_output)

    # logger.info("Running brute force vs genetic algorithm comparison...")
    # comparison_output = comparison.run_test(output_dir, num_runs)
    # logger.info("Output saved to %s", comparison_output)


if __name__ == "__main__":
    run_all_experiments(num_runs=10)
