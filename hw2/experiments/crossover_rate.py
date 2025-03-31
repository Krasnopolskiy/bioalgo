import logging
import os

import numpy as np

from .base_experiment import AccuracyExperiment

logger = logging.getLogger(__name__)


def run_test(base_config, output_dir="results", num_runs=10):
    os.makedirs(output_dir, exist_ok=True)

    step = 0.1
    crossover_rates = np.arange(0, 1.1, step)

    experiment = AccuracyExperiment(
        param_name="crossover_rate",
        param_values=crossover_rates,
        base_config=base_config,
        output_dir=output_dir,
        num_runs=num_runs,
    )

    return experiment.run()


if __name__ == "__main__":
    from run_all_experiments import run_all_experiments

    run_all_experiments()
