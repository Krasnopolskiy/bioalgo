import logging
import os
from typing import Callable

import matplotlib.animation as animation
import numpy as np
from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)


def animate_population(
    generations_data: list[list[float]],
    fitness_function: Callable[[float], float],
    bounds: tuple[float, float],
    title: str = "Genetic Algorithm Animation",
    output_file: str = "genetic_animation.mp4",
):
    fig, ax = plt.subplots(figsize=(10, 6))

    x_vals = np.linspace(bounds[0] - 1, bounds[1] + 1, 1000)
    y_vals = [fitness_function(x) for x in x_vals]

    ax.plot(x_vals, y_vals, "b-", alpha=0.5, label="Fitness Function")

    scatter = ax.scatter([], [], color="red", alpha=0.7, s=50, label="Individuals")

    ax.set_xlim(bounds[0] - 1, bounds[1] + 1)
    ax.set_ylim(min(y_vals) - 1, max(y_vals) + 1)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(title)
    ax.legend()

    generation_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

    def init():
        scatter.set_offsets(np.empty((0, 2)))
        generation_text.set_text("")
        return scatter, generation_text

    def update(frame):
        individuals = generations_data[frame]
        fitness_values = [fitness_function(ind) for ind in individuals]
        points = np.column_stack((individuals, fitness_values))

        scatter.set_offsets(points)
        generation_text.set_text("Generation: %d" % (frame + 1))
        return scatter, generation_text

    anim = animation.FuncAnimation(fig, update, frames=len(generations_data), init_func=init, blit=True, interval=200)

    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)

    try:
        anim.save(output_file, writer="ffmpeg", fps=5, dpi=100)
    except Exception as e:
        logger.error("Error using ffmpeg: %s", e)
        gif_output = output_file.replace(".mp4", ".gif")
        try:
            anim.save(gif_output, writer="pillow", fps=5, dpi=100)
            output_file = gif_output
            logger.info("Saved as GIF instead: %s", gif_output)
        except Exception as e2:
            logger.error("Error saving animation: %s", e2)
            frames_dir = os.path.join(os.path.dirname(output_file), "frames")
            os.makedirs(frames_dir, exist_ok=True)
            logger.info("Saving individual frames to %s", frames_dir)
            for i in range(len(generations_data)):
                update(i)
                plt.savefig(os.path.join(frames_dir, f"generation_{i+1:03d}.png"))
            output_file = frames_dir

    plt.close(fig)
    logger.info("Animation process completed. Output: %s", output_file)

    return output_file


def plot_3d_surface(x_values, y_values, z_values, x_label, y_label, z_label, title, output_file):
    # Swap axes to get the desired orientation
    Y, X = np.meshgrid(y_values, x_values)

    if z_values.shape[0] == len(x_values) and z_values.shape[1] == len(y_values):
        z_values = z_values
    else:
        z_values = z_values.T

    # Negate Z values to flip the direction (making lower values appear higher)
    Z = -z_values

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8)

    # Set the view to show generations in front and parameter on the left
    ax.view_init(elev=30, azim=45)

    # Customize the appearance
    ax.set_xlabel(x_label, labelpad=10)  # Parameter
    ax.set_ylabel(y_label, labelpad=10)  # Generation
    ax.set_zlabel(z_label, labelpad=10)  # Fitness
    ax.set_title(title, pad=20)

    # Invert z-axis to show fitness from top to bottom
    ax.invert_zaxis()

    # Add color bar
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, pad=0.1)
    cbar.set_label(z_label, rotation=90, labelpad=10)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save with higher DPI for better quality
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()


def plot_2d_line(x_values, y_values, x_label, y_label, title, output_file):
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker="o")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()
