import numpy as np

from lib.config import Config

from .base_experiment import AccuracyExperiment


def run_test(base_config: Config, output_dir: str = "results", num_runs: int = 10) -> str:
    step = 0.1
    mutation_rates = np.arange(0, 1, step)

    experiment = AccuracyExperiment(
        param_name="mutation_rate",
        param_values=mutation_rates,
        base_config=base_config,
        output_dir=output_dir,
        num_runs=num_runs,
    )

    return experiment.run()


if __name__ == "__main__":
    from run_all_experiments import run_all_experiments

    run_all_experiments()
