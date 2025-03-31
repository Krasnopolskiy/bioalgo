import numpy as np

from .base_experiment import AccuracyExperiment


def run_test(base_config, output_dir="results", num_runs=10):
    step = 50
    population_sizes = np.arange(50, 500, step)

    experiment = AccuracyExperiment(
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
