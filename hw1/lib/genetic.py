import random
from typing import Callable

import numpy as np

from lib.config import Config


class GeneticAlgorithm:
    def __init__(self, fitness_function: Callable[[float], float], config: Config):
        self.fitness_function = fitness_function
        self.config = config

        self.best_individual_per_generation = []
        self.avg_fitness_per_generation = []

        self.populations = []
        self.decoded_populations = []

    def run(self) -> tuple[float, np.ndarray]:
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

        self.best_individual_per_generation.append((best_individual, best_score))
        self.avg_fitness_per_generation.append(np.mean(fitness_scores))

        elite_indices = np.argsort(fitness_scores)[: self.config.elite_size]

        new_population = []
        for idx in elite_indices:
            new_population.append(population[idx])

        parents = self.select_parents(population, fitness_scores)
        while len(new_population) < self.config.population_size:
            if random.random() < self.config.crossover_rate:
                individuals = self.crossover(parents)
            else:
                individual = random.choice(parents)
                individuals = [individual.copy()]

            new_population += [self.mutate(individual) for individual in individuals]

        return new_population[: self.config.population_size]

    def crossover(self, parents: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)

        crossover_point = random.randint(0, self.config.precision - 1)
        child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])

        return child1, child2

    def mutate(self, individual: np.ndarray) -> np.ndarray:
        for i in range(len(individual)):
            if random.random() < self.config.mutation_rate:
                individual[i] = 1 - individual[i]
        return individual

    def decode(self, individual: np.ndarray) -> float:
        decimal_value = 0
        for bit in individual:
            decimal_value = decimal_value * 2 + bit

        min_bound, max_bound = self.config.bounds
        normalized_value = decimal_value / (2**self.config.precision - 1)
        return min_bound + normalized_value * (max_bound - min_bound)

    def get_fitness_scores(self, population: list[np.ndarray]) -> np.ndarray:
        return np.array([self.fitness(individual) for individual in population])

    def get_best_individual(self, fitness_scores: np.ndarray, population: list[np.ndarray]) -> tuple[float, np.ndarray]:
        best_idx = np.argmin(fitness_scores)
        best_individual = self.decode(population[best_idx])
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
        x = self.decode(individual)
        return self.fitness_function(x)

    def initialize(self) -> list[np.ndarray]:
        return [np.random.randint(0, 2, self.config.precision) for _ in range(self.config.population_size)]

    def store(self, population: list[np.ndarray]):
        self.populations.append(population.copy())
        self.decoded_populations.append([self.decode(individual) for individual in population])

    def get_history(self):
        return {
            "best_individuals": self.best_individual_per_generation,
            "avg_fitness": self.avg_fitness_per_generation,
            "populations": self.decoded_populations,
        }
