import random
import csv
import logging
from pathlib import Path

BASE_DIR = Path("data")
N = 24
VECTORS_COUNT = 50
PROBLEMS_PER_VECTOR = 10
MIN_RATIO = 0.1
MAX_RATIO = 0.5

# Table of variants
VARIANTS = [
    {"number": 1, "n": 24, "divider": 0.8, "modulo": False},
    {"number": 2, "n": 24, "divider": 1.0, "modulo": False},
    {"number": 3, "n": 24, "divider": 1.2, "modulo": False},
    {"number": 4, "n": 24, "divider": 1.4, "modulo": False},
    {"number": 5, "n": 24, "divider": 0.8, "modulo": True},
    {"number": 6, "n": 24, "divider": 1.0, "modulo": True},
    {"number": 7, "n": 24, "divider": 1.2, "modulo": True},
    {"number": 8, "n": 24, "divider": 1.4, "modulo": True},
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def calculate_a_max(n: int, divider: float) -> int:
    return int(2 ** (n / divider))


def generate_knapsack_vector(n: int, a_max: int) -> list:
    return [random.randint(1, a_max) for _ in range(n)]


def generate_multiple_vectors(n: int, a_max: int, count: int) -> list:
    return [generate_knapsack_vector(n, a_max) for _ in range(count)]


def save_vectors_to_file(vectors: list, a_max: int, path: Path) -> None:
    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["Номер вектора", "Вектор", "a_max"])
        for i, vector in enumerate(vectors, 1):
            writer.writerow([i, vector, a_max])


def generate_knapsack_problem(vector: list, min_ratio: float, max_ratio: float) -> tuple:
    n = len(vector)
    num_items = random.randint(int(n * min_ratio), int(n * max_ratio))
    selected_indices = random.sample(range(n), num_items)
    selected_items = [vector[i] for i in selected_indices]
    target_weight = sum(selected_items)
    ratio = num_items / n
    return (vector, target_weight, ratio)


def generate_problems_for_vector(vector: list, num_problems: int) -> list:
    return [generate_knapsack_problem(vector, MIN_RATIO, MAX_RATIO) for _ in range(num_problems)]


def generate_all_problems(vectors: list, problems_per_vector: int) -> list:
    all_problems = []
    for i, vector in enumerate(vectors):
        problems = generate_problems_for_vector(vector, problems_per_vector)
        for problem in problems:
            all_problems.append((i + 1, problem[0], problem[1], problem[2]))
    return all_problems


def save_problems_to_file(problems: list, path: Path) -> None:
    with open(path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["Номер задачи", "Номер вектора", "Целевой вес", "Доля предметов"])
        for i, (vector_num, _, target, ratio) in enumerate(problems, 1):
            writer.writerow([i, vector_num, target, "%.2f" % ratio])


def generate_for_variant(variant: dict) -> None:
    variant_num = variant["number"]
    n = variant["n"]
    divider = variant["divider"]
    a_max = calculate_a_max(n, divider)

    # Create directory for this variant
    option_dir = BASE_DIR / f"option{variant_num}"
    option_dir.mkdir(exist_ok=True, parents=True)

    # Generate and save vectors
    vectors = generate_multiple_vectors(n, a_max, VECTORS_COUNT)
    vectors_path = option_dir / "knapsack_vectors.csv"
    save_vectors_to_file(vectors, a_max, vectors_path)

    # Generate and save problems
    all_problems = generate_all_problems(vectors, PROBLEMS_PER_VECTOR)
    problems_path = option_dir / "knapsack_problems.csv"
    save_problems_to_file(all_problems, problems_path)

    logging.info(
        "Generated data for variant %d: n=%d, divider=%.1f, a_max=%d, modulo=%s, vectors=%d, problems=%d",
        variant_num,
        n,
        divider,
        a_max,
        "yes" if variant["modulo"] else "no",
        VECTORS_COUNT,
        len(all_problems),
    )


def main() -> None:
    for variant in VARIANTS:
        generate_for_variant(variant)
    logging.info("Data generation completed for all variants")


if __name__ == "__main__":
    main()
