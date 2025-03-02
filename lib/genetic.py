import random
from typing import Callable, List, Tuple

import numpy as np


class GeneticAlgorithm:
    def __init__(
        self,
        fitness_function: Callable[[float], float],
        bounds: Tuple[float, float],
        population_size: int = 100,
        generations: int = 100,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elite_size: int = 5,
        precision: int = 32,
    ):
        self.fitness_function = fitness_function
        self.bounds = bounds
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.precision = precision

        self.best_individual_per_generation = []
        self.avg_fitness_per_generation = []
        self.current_generation = 0

    def run(self) -> tuple[float, np.ndarray]:
        population = self._initialize_population()

        for generation in range(self.generations):
            self.current_generation = generation + 1

            fitness_scores = np.array([self._evaluate_fitness(individual) for individual in population])

            best_idx = np.argmin(fitness_scores)
            best_individual = self._decode_individual(population[best_idx])
            self.best_individual_per_generation.append((best_individual, fitness_scores[best_idx]))
            self.avg_fitness_per_generation.append(np.mean(fitness_scores))

            parents = self._select_parents(population, fitness_scores)

            new_population = []

            elite_indices = np.argsort(fitness_scores)[: self.elite_size]
            for idx in elite_indices:
                new_population.append(population[idx])

            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    parent1 = random.choice(parents)
                    parent2 = random.choice(parents)
                    child1, child2 = self._crossover(parent1, parent2)

                    child1 = self._mutate(child1)
                    child2 = self._mutate(child2)

                    new_population.append(child1)
                    if len(new_population) < self.population_size:
                        new_population.append(child2)
                else:
                    parent = random.choice(parents)
                    child = self._mutate(parent.copy())
                    new_population.append(child)

            population = new_population

        fitness_scores = np.array([self._evaluate_fitness(individual) for individual in population])
        best_idx = np.argmin(fitness_scores)
        best_individual = self._decode_individual(population[best_idx])

        return best_individual, fitness_scores[best_idx]

    def _initialize_population(self) -> List[np.ndarray]:
        return [np.random.randint(0, 2, self.precision) for _ in range(self.population_size)]

    def _decode_individual(self, individual: np.ndarray) -> float:
        decimal_value = 0
        for bit in individual:
            decimal_value = decimal_value * 2 + bit

        min_bound, max_bound = self.bounds
        normalized_value = decimal_value / (2**self.precision - 1)
        return min_bound + normalized_value * (max_bound - min_bound)

    def _evaluate_fitness(self, individual: np.ndarray) -> float:
        x = self._decode_individual(individual)
        return self.fitness_function(x)

    def _select_parents(self, population: List[np.ndarray], fitness_scores: np.ndarray) -> List[np.ndarray]:
        tournament_size = 3
        parents = []

        for _ in range(self.population_size):
            tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
            tournament_fitnesses = [fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmin(tournament_fitnesses)]
            parents.append(population[winner_idx])

        return parents

    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        crossover_point = random.randint(0, self.precision - 1)
        child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
        return child1, child2

    def _mutate(self, individual: np.ndarray) -> np.ndarray:
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                individual[i] = 1 - individual[i]
        return individual

    def get_history(self):
        return {
            "best_individuals": self.best_individual_per_generation,
            "avg_fitness": self.avg_fitness_per_generation,
        }
