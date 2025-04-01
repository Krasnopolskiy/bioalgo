import ast
import csv
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path("data")
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
POPULATION_SIZE = 200

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def calculate_a_max(n: int, divider: float) -> int:
    return int(2 ** (n / divider))


def load_brute_force_results(path: Path) -> dict:
    results = {}
    if not path.exists():
        logging.warning(f"File not found: {path}")
        return results

    try:
        with open(path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                if row:
                    problem_idx = int(row[0])
                    first_solution_time = float(row[1])
                    all_solutions_time = float(row[2])
                    solutions_count = int(row[3])

                    results[problem_idx] = {
                        "first_solution_time": first_solution_time,
                        "all_solutions_time": all_solutions_time,
                        "solutions_count": solutions_count,
                    }
    except Exception as e:
        logging.error(f"Error loading brute force results: {e}")

    return results


def load_genetic_results(path: Path) -> dict:
    results = {}
    if not path.exists():
        logging.warning(f"File not found: {path}")
        return results

    try:
        with open(path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                if row:
                    problem_idx = int(row[0])
                    time_used = float(row[1])
                    min_fitness = int(row[2])
                    stop_reason = row[3]
                    last_generation = int(row[4])

                    results[problem_idx] = {
                        "time_used": time_used,
                        "min_fitness": min_fitness,
                        "stop_reason": stop_reason,
                        "last_generation": last_generation,
                    }
    except Exception as e:
        logging.error(f"Error loading genetic results: {e}")

    return results


def load_vectors(path: Path) -> dict:
    vectors = {}
    try:
        with open(path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                vector_idx = int(row[0])
                vector = ast.literal_eval(row[1])
                a_max = int(row[2])
                vectors[vector_idx] = {"vector": vector, "a_max": a_max}
    except Exception as e:
        logging.error(f"Error loading vectors: {e}")

    return vectors


def load_problems(path: Path) -> list:
    problems = []
    try:
        with open(path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader)
            for row in reader:
                problem_idx = int(row[0])
                vector_idx = int(row[1])
                target = int(row[2])
                ratio = float(row[3])
                problems.append(
                    {"problem_idx": problem_idx, "vector_idx": vector_idx, "target": target, "ratio": ratio}
                )
    except Exception as e:
        logging.error(f"Error loading problems: {e}")

    return problems


def calculate_statistics(variant_num: int) -> dict:
    variant = next((v for v in VARIANTS if v["number"] == variant_num), None)
    if not variant:
        logging.error(f"Invalid variant number: {variant_num}")
        return {}

    option_dir = BASE_DIR / f"option{variant_num}"

    brute_force_results = load_brute_force_results(option_dir / "brute_force_results.csv")
    genetic_results = load_genetic_results(option_dir / "genetic_results.csv")
    vectors = load_vectors(option_dir / "knapsack_vectors.csv")
    problems = load_problems(option_dir / "knapsack_problems.csv")

    logging.info(f"Loaded {len(brute_force_results)} brute force results, {len(genetic_results)} genetic results")

    n = variant["n"]
    divider = variant["divider"]
    a_max = calculate_a_max(n, divider)

    first_solution_times = [
        brute_force_results.get(p["problem_idx"], {}).get("first_solution_time", 0)
        for p in problems
        if p["problem_idx"] in brute_force_results
    ]

    all_solutions_times = [
        brute_force_results.get(p["problem_idx"], {}).get("all_solutions_time", 0)
        for p in problems
        if p["problem_idx"] in brute_force_results
    ]

    exact_solution_genetic = [
        genetic_results.get(p["problem_idx"], {}).get("time_used", 0)
        for p in problems
        if p["problem_idx"] in genetic_results and genetic_results[p["problem_idx"]]["min_fitness"] == 0
    ]

    total_problems = len(problems)
    solved_exact_genetic = sum(
        1
        for p in problems
        if p["problem_idx"] in genetic_results and genetic_results[p["problem_idx"]]["min_fitness"] == 0
    )
    exact_solution_ratio = solved_exact_genetic / total_problems if total_problems > 0 else 0

    logging.info(f"Variant {variant_num}: {solved_exact_genetic}/{total_problems} solved exactly by GA")

    stats = {
        "n": {"mean": n, "variance": 0, "std_dev": 0},
        "a_max": {"mean": a_max, "variance": 0, "std_dev": 0},
        "first_solution_time": {
            "mean": np.mean(first_solution_times) if first_solution_times else None,
            "variance": np.var(first_solution_times) if len(first_solution_times) > 1 else None,
            "std_dev": np.std(first_solution_times) if len(first_solution_times) > 1 else None,
        },
        "all_solutions_time": {
            "mean": np.mean(all_solutions_times) if all_solutions_times else None,
            "variance": np.var(all_solutions_times) if len(all_solutions_times) > 1 else None,
            "std_dev": np.std(all_solutions_times) if len(all_solutions_times) > 1 else None,
        },
        "exact_solution_genetic_time": {
            "mean": np.mean(exact_solution_genetic) if exact_solution_genetic else None,
            "variance": np.var(exact_solution_genetic) if len(exact_solution_genetic) > 1 else None,
            "std_dev": np.std(exact_solution_genetic) if len(exact_solution_genetic) > 1 else None,
        },
        "exact_solution_ratio": {"mean": exact_solution_ratio, "variance": 0, "std_dev": 0},
        "population_size": {"mean": POPULATION_SIZE, "variance": 0, "std_dev": 0},
    }

    return stats


def save_statistics(statistics: dict, path: Path) -> None:
    try:
        with open(path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["", "Среднее значение", "Дисперсия", "Среднее квадратичное откл."])

            for param, values in statistics.items():
                mean_value = values["mean"] if values["mean"] is not None else ""
                variance = values["variance"] if values["variance"] is not None else ""
                std_dev = values["std_dev"] if values["std_dev"] is not None else ""

                writer.writerow([param, mean_value, variance, std_dev])

        logging.info(f"Statistics saved to {path}")
    except Exception as e:
        logging.error(f"Error saving statistics to file: {e}")


def create_plots(variant_stats: dict) -> None:
    plots_dir = BASE_DIR / "plots"
    plots_dir.mkdir(exist_ok=True, parents=True)

    a_max_values_no_modulo = []
    a_max_values_with_modulo = []
    first_solution_times_no_modulo = []
    first_solution_times_with_modulo = []
    all_solutions_times_no_modulo = []
    all_solutions_times_with_modulo = []
    genetic_times_no_modulo = []
    genetic_times_with_modulo = []
    exact_solution_ratios_no_modulo = []
    exact_solution_ratios_with_modulo = []
    variant_numbers_no_modulo = []
    variant_numbers_with_modulo = []

    # Sort variants by a_max and group by modulo
    sorted_variants = sorted(variant_stats.items(), key=lambda x: x[1]["a_max"]["mean"])

    # Separate data for modulo and non-modulo variants
    for variant_num, stats in sorted_variants:
        # Get modulo status from variant definition
        variant = next((v for v in VARIANTS if v["number"] == variant_num), None)
        if not variant:
            continue

        uses_modulo = variant["modulo"]

        # Append to appropriate lists based on modulo status
        if uses_modulo:
            a_max_values_with_modulo.append(stats["a_max"]["mean"])
            variant_numbers_with_modulo.append(variant_num)

            first_solution_times_with_modulo.append(
                stats["first_solution_time"]["mean"] if stats["first_solution_time"]["mean"] is not None else 0
            )

            all_solutions_times_with_modulo.append(
                stats["all_solutions_time"]["mean"] if stats["all_solutions_time"]["mean"] is not None else 0
            )

            genetic_times_with_modulo.append(
                stats["exact_solution_genetic_time"]["mean"]
                if stats["exact_solution_genetic_time"]["mean"] is not None
                else 0
            )

            exact_solution_ratios_with_modulo.append(stats["exact_solution_ratio"]["mean"])
        else:
            a_max_values_no_modulo.append(stats["a_max"]["mean"])
            variant_numbers_no_modulo.append(variant_num)

            first_solution_times_no_modulo.append(
                stats["first_solution_time"]["mean"] if stats["first_solution_time"]["mean"] is not None else 0
            )

            all_solutions_times_no_modulo.append(
                stats["all_solutions_time"]["mean"] if stats["all_solutions_time"]["mean"] is not None else 0
            )

            genetic_times_no_modulo.append(
                stats["exact_solution_genetic_time"]["mean"]
                if stats["exact_solution_genetic_time"]["mean"] is not None
                else 0
            )

            exact_solution_ratios_no_modulo.append(stats["exact_solution_ratio"]["mean"])

    # Create evenly spaced x-coordinates for plotting
    x_positions_no_modulo = list(range(len(a_max_values_no_modulo)))
    x_positions_with_modulo = list(range(len(a_max_values_with_modulo)))

    # Create combined list of all a_max values for x-axis labeling
    all_a_max_values = sorted(set(a_max_values_no_modulo + a_max_values_with_modulo))
    all_x_positions = list(range(len(all_a_max_values)))
    x_labels = [str(val) for val in all_a_max_values]

    try:
        # Create mapping from a_max value to position in the all_x_positions list
        a_max_to_position = {a_max: pos for pos, a_max in zip(all_x_positions, all_a_max_values)}

        # Map actual a_max values to their positions in the combined list
        plot_positions_no_modulo = [a_max_to_position[a_max] for a_max in a_max_values_no_modulo]
        plot_positions_with_modulo = [a_max_to_position[a_max] for a_max in a_max_values_with_modulo]

        # 1. First solution time
        plt.figure(figsize=(10, 6))
        if plot_positions_no_modulo:
            plt.plot(plot_positions_no_modulo, first_solution_times_no_modulo, "o-", label="Без модуля", color="blue")
            for i, txt in enumerate(variant_numbers_no_modulo):
                plt.annotate(
                    f"В{txt}",
                    (plot_positions_no_modulo[i], first_solution_times_no_modulo[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                )

        if plot_positions_with_modulo:
            plt.plot(
                plot_positions_with_modulo, first_solution_times_with_modulo, "s--", label="С модулем", color="red"
            )
            for i, txt in enumerate(variant_numbers_with_modulo):
                plt.annotate(
                    f"В{txt}",
                    (plot_positions_with_modulo[i], first_solution_times_with_modulo[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                )

        plt.xlabel("a_max")
        plt.ylabel("Время (с)")
        plt.title("Зависимость среднего времени нахождения первого решения от a_max")
        plt.xticks(all_x_positions, x_labels)
        plt.grid(True)
        plt.legend()
        plt.savefig(plots_dir / "first_solution_time_vs_a_max.png")
        plt.close()

        # 2. All solutions time
        plt.figure(figsize=(10, 6))
        if plot_positions_no_modulo:
            plt.plot(plot_positions_no_modulo, all_solutions_times_no_modulo, "o-", label="Без модуля", color="blue")
            for i, txt in enumerate(variant_numbers_no_modulo):
                plt.annotate(
                    f"В{txt}",
                    (plot_positions_no_modulo[i], all_solutions_times_no_modulo[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                )

        if plot_positions_with_modulo:
            plt.plot(plot_positions_with_modulo, all_solutions_times_with_modulo, "s--", label="С модулем", color="red")
            for i, txt in enumerate(variant_numbers_with_modulo):
                plt.annotate(
                    f"В{txt}",
                    (plot_positions_with_modulo[i], all_solutions_times_with_modulo[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                )

        plt.xlabel("a_max")
        plt.ylabel("Время (с)")
        plt.title("Зависимость среднего времени нахождения всех решений от a_max")
        plt.xticks(all_x_positions, x_labels)
        plt.grid(True)
        plt.legend()
        plt.savefig(plots_dir / "all_solutions_time_vs_a_max.png")
        plt.close()

        # 3. Genetic algorithm time
        plt.figure(figsize=(10, 6))
        if plot_positions_no_modulo:
            plt.plot(plot_positions_no_modulo, genetic_times_no_modulo, "o-", label="Без модуля", color="blue")
            for i, txt in enumerate(variant_numbers_no_modulo):
                if genetic_times_no_modulo[i] > 0:
                    plt.annotate(
                        f"В{txt}",
                        (plot_positions_no_modulo[i], genetic_times_no_modulo[i]),
                        xytext=(5, 5),
                        textcoords="offset points",
                    )

        if plot_positions_with_modulo:
            plt.plot(plot_positions_with_modulo, genetic_times_with_modulo, "s--", label="С модулем", color="red")
            for i, txt in enumerate(variant_numbers_with_modulo):
                if genetic_times_with_modulo[i] > 0:
                    plt.annotate(
                        f"В{txt}",
                        (plot_positions_with_modulo[i], genetic_times_with_modulo[i]),
                        xytext=(5, 5),
                        textcoords="offset points",
                    )

        plt.xlabel("a_max")
        plt.ylabel("Время (с)")
        plt.title("Зависимость среднего времени нахождения точного решения ГА от a_max")
        plt.xticks(all_x_positions, x_labels)
        plt.grid(True)
        plt.legend()
        plt.savefig(plots_dir / "genetic_time_vs_a_max.png")
        plt.close()

        # 4. Exact solution ratio
        plt.figure(figsize=(10, 6))
        if plot_positions_no_modulo:
            plt.plot(plot_positions_no_modulo, exact_solution_ratios_no_modulo, "o-", label="Без модуля", color="blue")
            for i, txt in enumerate(variant_numbers_no_modulo):
                plt.annotate(
                    f"В{txt}",
                    (plot_positions_no_modulo[i], exact_solution_ratios_no_modulo[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                )

        if plot_positions_with_modulo:
            plt.plot(
                plot_positions_with_modulo, exact_solution_ratios_with_modulo, "s--", label="С модулем", color="red"
            )
            for i, txt in enumerate(variant_numbers_with_modulo):
                plt.annotate(
                    f"В{txt}",
                    (plot_positions_with_modulo[i], exact_solution_ratios_with_modulo[i]),
                    xytext=(5, 5),
                    textcoords="offset points",
                )

        plt.xlabel("a_max")
        plt.ylabel("Доля задач")
        plt.title("Зависимость доли успешно решённых ГА задач от a_max")
        plt.xticks(all_x_positions, x_labels)
        plt.grid(True)
        plt.legend()
        plt.savefig(plots_dir / "exact_solution_ratio_vs_a_max.png")
        plt.close()

        # 5. Algorithm comparison - separate by modulo/no modulo
        plt.figure(figsize=(12, 8))

        # Non-modulo variants
        if plot_positions_no_modulo:
            plt.plot(
                plot_positions_no_modulo,
                first_solution_times_no_modulo,
                "o-",
                label="Полный перебор (первое решение) - без модуля",
                color="blue",
            )
            plt.plot(
                plot_positions_no_modulo,
                all_solutions_times_no_modulo,
                "o--",
                label="Полный перебор (все решения) - без модуля",
                color="darkblue",
            )
            plt.plot(
                plot_positions_no_modulo,
                genetic_times_no_modulo,
                "o:",
                label="Генетический алгоритм - без модуля",
                color="lightblue",
            )

            # Add variant annotations
            for i, txt in enumerate(variant_numbers_no_modulo):
                max_time = max(
                    first_solution_times_no_modulo[i], all_solutions_times_no_modulo[i], genetic_times_no_modulo[i]
                )
                plt.annotate(
                    f"В{txt}", (plot_positions_no_modulo[i], max_time), xytext=(5, 5), textcoords="offset points"
                )

        # Modulo variants
        if plot_positions_with_modulo:
            plt.plot(
                plot_positions_with_modulo,
                first_solution_times_with_modulo,
                "s-",
                label="Полный перебор (первое решение) - с модулем",
                color="red",
            )
            plt.plot(
                plot_positions_with_modulo,
                all_solutions_times_with_modulo,
                "s--",
                label="Полный перебор (все решения) - с модулем",
                color="darkred",
            )
            plt.plot(
                plot_positions_with_modulo,
                genetic_times_with_modulo,
                "s:",
                label="Генетический алгоритм - с модулем",
                color="salmon",
            )

            # Add variant annotations
            for i, txt in enumerate(variant_numbers_with_modulo):
                max_time = max(
                    first_solution_times_with_modulo[i],
                    all_solutions_times_with_modulo[i],
                    genetic_times_with_modulo[i],
                )
                plt.annotate(
                    f"В{txt}", (plot_positions_with_modulo[i], max_time), xytext=(5, 5), textcoords="offset points"
                )

        plt.xlabel("a_max")
        plt.ylabel("Время (с)")
        plt.title("Сравнение времени работы алгоритмов в зависимости от a_max")
        plt.xticks(all_x_positions, x_labels)
        plt.grid(True)
        plt.legend()
        plt.savefig(plots_dir / "algorithm_comparison.png")
        plt.close()

        logging.info(f"Plots saved to {plots_dir}")
    except Exception as e:
        logging.error(f"Error creating plots: {e}")


def main() -> None:
    results_dir = BASE_DIR / "results"
    results_dir.mkdir(exist_ok=True, parents=True)

    variant_stats = {}

    with open(results_dir / "summary_statistics.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(
            [
                "Вариант",
                "n",
                "a_max",
                "divider",
                "modulo",
                "Среднее время нахождения первого решения",
                "Среднее время нахождения всех решений",
                "Среднее время нахождения точного решения ГА",
                "Доля точно решённых задач ГА",
                "Количество хромосом в поколении",
            ]
        )

    for variant_num in range(1, 9):
        logging.info(f"Processing statistics for variant {variant_num}")

        variant = next((v for v in VARIANTS if v["number"] == variant_num), None)
        if not variant:
            logging.error(f"Invalid variant number: {variant_num}")
            continue

        stats = calculate_statistics(variant_num)

        if stats:
            variant_stats[variant_num] = stats

            save_statistics(stats, results_dir / f"statistics_variant_{variant_num}.csv")

            with open(results_dir / "summary_statistics.csv", "a", newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter=",")

                first_time_mean = (
                    stats["first_solution_time"]["mean"] if stats["first_solution_time"]["mean"] is not None else ""
                )
                all_time_mean = (
                    stats["all_solutions_time"]["mean"] if stats["all_solutions_time"]["mean"] is not None else ""
                )
                genetic_time_mean = (
                    stats["exact_solution_genetic_time"]["mean"]
                    if stats["exact_solution_genetic_time"]["mean"] is not None
                    else ""
                )

                writer.writerow(
                    [
                        variant_num,
                        variant["n"],
                        stats["a_max"]["mean"],
                        variant["divider"],
                        "Да" if variant["modulo"] else "Нет",
                        first_time_mean,
                        all_time_mean,
                        genetic_time_mean,
                        stats["exact_solution_ratio"]["mean"],
                        POPULATION_SIZE,
                    ]
                )

    if variant_stats:
        create_plots(variant_stats)
        logging.info("Statistics processing completed")
    else:
        logging.warning("No statistics data available")


if __name__ == "__main__":
    main()
