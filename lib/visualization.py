import os
from typing import Callable, List, Tuple

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


def animate_population(
    generations_data: List[List[float]],
    fitness_function: Callable[[float], float],
    bounds: Tuple[float, float],
    title: str = "Genetic Algorithm Animation",
    output_file: str = "genetic_animation.mp4",
):
    """
    Create an animation showing the movement of individuals across generations.

    Args:
        generations_data: List of lists containing decoded individuals for each generation
        fitness_function: The fitness function used in the genetic algorithm
        bounds: The bounds of the search space (min, max)
        title: Title of the animation
        output_file: Path to save the animation file
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create x values for plotting the fitness function
    x_vals = np.linspace(bounds[0], bounds[1], 1000)
    y_vals = [fitness_function(x) for x in x_vals]

    # Plot the fitness function
    ax.plot(x_vals, y_vals, "b-", alpha=0.5, label="Fitness Function")

    # Set up the scatter plot for individuals
    scatter = ax.scatter([], [], color="red", alpha=0.7, s=50, label="Individuals")

    # Set plot properties
    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(min(y_vals) - 1, max(y_vals) + 1)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(title)
    ax.legend()

    # Generation text
    generation_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

    def init():
        scatter.set_offsets(np.empty((0, 2)))
        generation_text.set_text("")
        return scatter, generation_text

    def update(frame):
        # Get individuals for the current generation
        individuals = generations_data[frame]

        # Calculate fitness values for each individual
        fitness_values = [fitness_function(ind) for ind in individuals]

        # Create points for scatter plot
        points = np.column_stack((individuals, fitness_values))

        scatter.set_offsets(points)
        generation_text.set_text(f"Generation: {frame+1}")
        return scatter, generation_text

    # Create animation
    anim = animation.FuncAnimation(fig, update, frames=len(generations_data), init_func=init, blit=True, interval=200)

    # Save animation
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)

    try:
        # Try using ffmpeg first
        anim.save(output_file, writer="ffmpeg", fps=5, dpi=100)
    except Exception as e:
        print(f"Error using ffmpeg: {e}")
        # Fall back to pillow for gif output
        gif_output = output_file.replace(".mp4", ".gif")
        try:
            anim.save(gif_output, writer="pillow", fps=5, dpi=100)
            output_file = gif_output
            print(f"Saved as GIF instead: {gif_output}")
        except Exception as e2:
            print(f"Error saving animation: {e2}")
            # Last resort: save as a series of PNG frames
            frames_dir = os.path.join(os.path.dirname(output_file), "frames")
            os.makedirs(frames_dir, exist_ok=True)
            print(f"Saving individual frames to {frames_dir}")
            for i in range(len(generations_data)):
                update(i)
                plt.savefig(os.path.join(frames_dir, f"generation_{i+1:03d}.png"))
            output_file = frames_dir

    plt.close(fig)
    print(f"Animation process completed. Output: {output_file}")

    return output_file
