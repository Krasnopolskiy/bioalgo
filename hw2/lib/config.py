import dataclasses
import numpy as np


@dataclasses.dataclass
class Config:
    cities: np.ndarray
    population_size: int = 100
    generations: int = 100
    tournament_size: int = 3
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    elite_size: int = 5
