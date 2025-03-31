import random
from typing import Callable

import numpy as np

from lib.config import Config


class GeneticAlgorithm:
    def __init__(self, fitness_function: Callable[[np.ndarray], float], config: Config):
        self.fitness_function = fitness_function
        self.config = config

        self.best_individual_per_generation = []
        self.avg_fitness_per_generation = []

        self.populations = []
        self.fitness_per_generation = []

    def run(self) -> tuple[np.ndarray, float]:
        population = self.initialize()

        self.store(population)

        for generation in range(self.config.generations):
            population = self.process(population)
            self.store(population)

        fitness_scores = self.get_fitness_scores(population)
        best_individual, best_score = self.get_best_individual(fitness_scores, population)

        return best_individual, best_score

    def process(self, population: list[np.ndarray]) -> list[np.ndarray]:
        fitness_scores = self.get_fitness_scores(population)
        best_individual, best_score = self.get_best_individual(fitness_scores, population)

        self.best_individual_per_generation.append((best_individual.copy(), best_score))
        self.avg_fitness_per_generation.append(np.mean(fitness_scores))

        elite_indices = np.argsort(fitness_scores)[: self.config.elite_size]

        new_population = []
        for idx in elite_indices:
            new_population.append(population[idx].copy())

        parents = self.select_parents(population, fitness_scores)
        while len(new_population) < self.config.population_size:
            if random.random() < self.config.crossover_rate and len(parents) >= 2:
                individuals = self.crossover(parents)
            else:
                individual = random.choice(parents)
                individuals = [individual.copy()]

            new_population += [self.mutate(individual.copy()) for individual in individuals]

        return new_population[: self.config.population_size]

    def crossover(self, parents: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)

        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child1 = np.full(size, -1)
        child2 = np.full(size, -1)

        child1[start:end] = parent1[start:end]
        child2[start:end] = parent2[start:end]

        self._fill_remaining_positions(parent2, child1, start, end)
        self._fill_remaining_positions(parent1, child2, start, end)

        return child1, child2

    def _fill_remaining_positions(self, parent, child, start, end):
        size = len(parent)
        remaining = [item for item in parent if item not in child[start:end]]

        idx = end % size
        for value in remaining:
            while child[idx] != -1:
                idx = (idx + 1) % size
            child[idx] = value
            idx = (idx + 1) % size

    def mutate(self, individual: np.ndarray) -> np.ndarray:
        if random.random() < self.config.mutation_rate:
            idx1, idx2 = random.sample(range(len(individual)), 2)
            individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        return individual

    def get_fitness_scores(self, population: list[np.ndarray]) -> np.ndarray:
        return np.array([self.fitness(individual) for individual in population])

    def get_best_individual(self, fitness_scores: np.ndarray, population: list[np.ndarray]) -> tuple[np.ndarray, float]:
        best_idx = np.argmin(fitness_scores)
        best_individual = population[best_idx]
        return best_individual, fitness_scores[best_idx]

    def select_parents(self, population: list[np.ndarray], fitness_scores: np.ndarray) -> list[np.ndarray]:
        parents = []

        for _ in range(self.config.population_size):
            indices = np.random.choice(len(population), self.config.tournament_size, replace=False)
            fitnesses = [fitness_scores[i] for i in indices]
            winner_idx = indices[np.argmin(fitnesses)]
            parents.append(population[winner_idx])

        return parents

    def fitness(self, individual: np.ndarray) -> float:
        return self.fitness_function(individual)

    def initialize(self) -> list[np.ndarray]:
        population = []
        for _ in range(self.config.population_size):
            individual = np.arange(len(self.config.cities))
            np.random.shuffle(individual)
            population.append(individual)
        return population

    def store(self, population: list[np.ndarray]):
        self.populations.append([individual.copy() for individual in population])
        self.fitness_per_generation.append([self.fitness(individual) for individual in population])

    def get_history(self):
        return {
            "best_individuals": self.best_individual_per_generation,
            "avg_fitness": self.avg_fitness_per_generation,
            "populations": self.populations,
            "fitness": self.fitness_per_generation,
        }
