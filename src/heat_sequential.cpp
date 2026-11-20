#include <chrono>
#include <iomanip>
#include <iostream>
#include <vector>

int main() {
    constexpr int grid_size = 1000;
    constexpr int time_steps = 100;

    // Start with a cool surface and a warm spot in the center.
    std::vector<std::vector<double>> current(
        grid_size, std::vector<double>(grid_size, 20.0));
    std::vector<std::vector<double>> next = current;
    current[grid_size / 2][grid_size / 2] = 100.0;

    // Keep the outer edge at 20 degrees. Update interior cells only.
    const auto start_time = std::chrono::steady_clock::now();

    for (int step = 0; step < time_steps; ++step) {
        for (int row = 1; row < grid_size - 1; ++row) {
            for (int col = 1; col < grid_size - 1; ++col) {
                next[row][col] = 0.25 * (
                    current[row - 1][col] + current[row + 1][col] +
                    current[row][col - 1] + current[row][col + 1]);
            }
        }

        // Swap the buffers so this step becomes the input to the next one.
        current.swap(next);
    }

    const auto end_time = std::chrono::steady_clock::now();
    const std::chrono::duration<double, std::milli> elapsed_time =
        end_time - start_time;

    std::cout << "Center temperature after " << time_steps
              << " steps: " << std::fixed << std::setprecision(2)
              << current[grid_size / 2][grid_size / 2] << " degrees\n";
    std::cout << "Simulation time: " << elapsed_time.count() << " ms\n";
}