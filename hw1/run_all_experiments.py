import logging
import os
import time

import numpy as np

from experiments.base_experiment import AccuracyExperiment, TimeExperiment
from lib.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_experiments(output_dir: str, num_runs: int) -> list[AccuracyExperiment]:
    base_config = Config(
        bounds=(-9.6, 9.1),
        population_size=100,
        generations=30,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.1,
        elite_size=5,
        precision=15,
    )
    params = {
        "base_config": base_config,
        "output_dir": output_dir,
        "num_runs": num_runs,
    }

    experiments = [
        AccuracyExperiment(param_name="mutation_rate", param_values=np.arange(0, 1, 0.1), **params),
        AccuracyExperiment(param_name="crossover_rate", param_values=np.arange(0, 1, 0.1), **params),
        AccuracyExperiment(param_name="population_size", param_values=np.arange(50, 500, 50), **params),
        TimeExperiment(param_name="population_size", param_values=np.arange(50, 500, 50), **params),
    ]

    return experiments


def run_all_experiments(output_dir: str = "results", num_runs: int = 1) -> dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()

    logger.info("Running all experiments with %d runs each", num_runs)

    experiments = create_experiments(output_dir, num_runs)
    results = {}

    for experiment in experiments:
        param_name = experiment.param_name
        logger.info(f"Running {param_name} experiment...")
        output_file = experiment.run()
        logger.info(f"{param_name} experiment completed. Results saved to {output_file}")
        results[param_name] = output_file

    total_time = time.time() - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    logger.info("All experiments completed successfully!")
    logger.info("Total execution time: %dh %dm %.2fs", int(hours), int(minutes), seconds)

    return results


if __name__ == "__main__":
    run_all_experiments()
