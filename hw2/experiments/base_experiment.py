import logging
import os

import numpy as np
from lib.config import Config
from lib.genetic import GeneticAlgorithm
from lib.visualization import plot_2d_line, plot_3d_surface

logger = logging.getLogger(__name__)


def calculate_distance(tour: np.ndarray) -> float:
    total_distance = 0
    cities = cities_global

    for i in range(len(tour)):
        from_city = tour[i]
        to_city = tour[(i + 1) % len(tour)]
        distance = np.linalg.norm(cities[from_city] - cities[to_city])
        total_distance += distance

    return total_distance


class BaseExperiment:
    def __init__(
        self,
        param_name: str,
        param_values: np.ndarray,
        base_config: Config,
        output_dir: str = "results",
        num_runs: int = 10,
    ):
        self.param_name = param_name
        self.param_values = param_values
        self.base_config = base_config
        self.output_dir = output_dir
        self.num_runs = num_runs

        global cities_global
        cities_global = base_config.cities

    def _create_config(self, param_value: float) -> Config:
        config = self.base_config.__dict__.copy()
        config[self.param_name] = param_value
        if self.param_name == "population_size":
            config["elite_size"] = max(1, int(param_value * 0.05))
        return type(self.base_config)(**config)

    def _run_experiment(self, param_value: float) -> list[float] | float:
        raise NotImplementedError

    def _process_results(self, results: list[list[float]]) -> np.ndarray:
        raise NotImplementedError

    def _create_visualization(self, processed_results: np.ndarray) -> str:
        raise NotImplementedError

    def run(self) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        all_results = []

        for param_value in self.param_values:
            param_results = []
            for _ in range(self.num_runs):
                result = self._run_experiment(param_value)
                param_results.append(result)
            all_results.append(param_results)

        processed_results = self._process_results(all_results)
        return self._create_visualization(processed_results)


class AccuracyExperiment(BaseExperiment):
    def _run_experiment(self, param_value: float) -> list[float]:
        config = self._create_config(param_value)
        ga = GeneticAlgorithm(fitness_function=calculate_distance, config=config)
        ga.run()
        history = ga.get_history()
        return [score for _, score in history["best_individuals"]]

    def _process_results(self, all_results: list[list[float]]) -> np.ndarray:
        results = np.array(all_results)
        return np.mean(results, axis=1)

    def _create_visualization(self, processed_results: np.ndarray) -> str:
        output_file = os.path.join(self.output_dir, f"{self.param_name}_accuracy.png")
        generations = np.arange(1, self.base_config.generations + 1)

        plot_3d_surface(
            x_values=self.param_values,
            y_values=generations,
            z_values=processed_results,
            x_label=self.param_name,
            y_label="Generation",
            z_label="Distance",
            title=f"TSP Distance vs {self.param_name} and Generation",
            output_file=output_file,
        )
        return output_file


class TimeExperiment(BaseExperiment):
    def _run_experiment(self, param_value: float) -> float:
        import time

        config = self._create_config(param_value)
        ga = GeneticAlgorithm(fitness_function=calculate_distance, config=config)

        start_time = time.time()
        ga.run()
        return time.time() - start_time

    def _process_results(self, all_results: list[list[float]]) -> np.ndarray:
        return np.mean(all_results, axis=1)

    def _create_visualization(self, processed_results: np.ndarray) -> str:
        output_file = os.path.join(self.output_dir, f"{self.param_name}_time.png")

        plot_2d_line(
            x_values=self.param_values,
            y_values=processed_results,
            x_label=self.param_name.title(),
            y_label="Average Execution Time (s)",
            title=f"{self.param_name.title()} vs Execution Time",
            output_file=output_file,
        )
        return output_file
