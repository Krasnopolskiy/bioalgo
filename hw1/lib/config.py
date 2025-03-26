import dataclasses


@dataclasses.dataclass
class Config:
    bounds: tuple[float, float]
    population_size: int = 100
    generations: int = 100
    tournament_size: int = 3
    crossover_rate: float = 0.8
    mutation_rate: float = 0.1
    elite_size: int = 5
    precision: int = 32
