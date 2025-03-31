import ast
import csv
import fcntl
import logging
import multiprocessing
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = Path("data")
NUM_PROCESSES = 15

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


def load_problems(path: Path) -> list:
    problems = []
    with open(path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for i, row in enumerate(reader, 1):
            problem_idx = int(row[0])
            vector_idx = int(row[1])
            target = int(row[2])
            ratio = float(row[3])
            problems.append((problem_idx, vector_idx, target, ratio))
    return problems


def load_vectors(path: Path) -> dict:
    vectors = {}
    with open(path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            vector_idx = int(row[0])
            vector = ast.literal_eval(row[1])
            vectors[vector_idx] = vector
    return vectors


def load_existing_results(path: Path) -> set:
    if not path.exists():
        with open(path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(
                ["Номер задачи", "Время нахождения первого решения", "Время нахождения всех решений", "Число решений"]
            )
        return set()

    solved_problems = set()
    with open(path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            if row:
                solved_problems.add(int(row[0]))
    return solved_problems


def is_solution_fast(vector: list, mask: int, target_mod: int, modulo: int, precomp_mods: list) -> bool:
    total_weight = 0
    for i in range(len(vector)):
        if mask & (1 << i):
            total_weight = (total_weight + precomp_mods[i]) % modulo
    return total_weight == target_mod


def is_solution_no_modulo(vector: list, mask: int, target: int) -> bool:
    total_weight = 0
    for i in range(len(vector)):
        if mask & (1 << i):
            total_weight += vector[i]
    return total_weight == target


def brute_force_solve(vector: list, target: int, use_modulo: bool) -> tuple:
    n = len(vector)
    first_solution_time = 0
    all_solutions = []
    start_time = time.time()

    if use_modulo:
        modulo = max(vector) + 1
        target_mod = target % modulo
        precomp_mods = [v % modulo for v in vector]

        for mask in range(1, 1 << n):
            if is_solution_fast(vector, mask, target_mod, modulo, precomp_mods):
                if not all_solutions:
                    first_solution_time = time.time() - start_time
                all_solutions.append(mask)
    else:
        for mask in range(1, 1 << n):
            if is_solution_no_modulo(vector, mask, target):
                if not all_solutions:
                    first_solution_time = time.time() - start_time
                all_solutions.append(mask)

    total_time = time.time() - start_time
    return first_solution_time, total_time, len(all_solutions), all_solutions


def save_result_to_file(result: tuple, path: Path) -> None:
    problem_idx, first_time, total_time, solutions_count = result
    with open(path, "a", newline="") as csvfile:
        fcntl.flock(csvfile, fcntl.LOCK_EX)
        try:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow([problem_idx, "%.6f" % first_time, "%.6f" % total_time, solutions_count])
        finally:
            fcntl.flock(csvfile, fcntl.LOCK_UN)


def solve_single_problem(args: tuple) -> tuple:
    problem_idx, vector_idx, target, ratio, vector, use_modulo, results_path = args
    first_time, total_time, solutions_count, solutions = brute_force_solve(vector, target, use_modulo)

    decoded_solutions = []
    for mask in solutions:
        solution = [1 if mask & (1 << i) else 0 for i in range(len(vector))]
        decoded_solutions.append(solution)

    result = (problem_idx, first_time, total_time, solutions_count)
    save_result_to_file(result, results_path)
    logging.info("Solved problem %d: found %d solutions in %.4f seconds", problem_idx, solutions_count, total_time)
    return result


def solve_all_problems_parallel(
    problems: list, vectors: dict, solved_problems: set, use_modulo: bool, results_path: Path
) -> None:
    unsolved_problems = [p for p in problems if p[0] not in solved_problems]
    if not unsolved_problems:
        logging.info("All problems already solved")
        return

    problem_args = [(p[0], p[1], p[2], p[3], vectors[p[1]], use_modulo, results_path) for p in unsolved_problems]
    logging.info("Starting %d processes for %d unsolved problems", NUM_PROCESSES, len(problem_args))

    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        pool.map(solve_single_problem, problem_args)


def solve_for_variant(variant_num: int) -> None:
    variant = next((v for v in VARIANTS if v["number"] == variant_num), None)
    if not variant:
        logging.error(f"Invalid variant number: {variant_num}")
        return

    option_dir = BASE_DIR / f"option{variant_num}"

    vectors_path = option_dir / "knapsack_vectors.csv"
    problems_path = option_dir / "knapsack_problems.csv"
    results_path = option_dir / "brute_force_results.csv"

    use_modulo = variant["modulo"]

    vectors = load_vectors(vectors_path)
    logging.info("Loaded %d knapsack vectors for variant %d", len(vectors), variant_num)

    problems = load_problems(problems_path)
    logging.info("Loaded %d knapsack problems for variant %d", len(problems), variant_num)

    solved_problems = load_existing_results(results_path)
    logging.info("Found %d already solved problems for variant %d", len(solved_problems), variant_num)

    solve_all_problems_parallel(problems, vectors, solved_problems, use_modulo, results_path)
    logging.info("Completed brute force solutions for variant %d", variant_num)


def main() -> None:
    if multiprocessing.get_start_method() != "spawn":
        multiprocessing.set_start_method("spawn", force=True)

    for variant in range(8):
        solve_for_variant(variant + 1)


if __name__ == "__main__":
    main()
