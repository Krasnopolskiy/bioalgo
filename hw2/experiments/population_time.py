import numpy as np
from lib.config import Config

from .base_experiment import TimeExperiment


def run_test(base_config: Config, output_dir: str = "results", num_runs: int = 10) -> str:
    step = 50
    population_sizes = np.arange(50, 500, step)

    experiment = TimeExperiment(
        param_name="population_size",
        param_values=population_sizes,
        base_config=base_config,
        output_dir=output_dir,
        num_runs=num_runs,
    )

    return experiment.run()


if __name__ == "__main__":
    from run_all_experiments import run_all_experiments

    run_all_experiments()
