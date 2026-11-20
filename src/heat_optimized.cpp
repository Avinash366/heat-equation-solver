#include <chrono>
#include <iomanip>
#include <iostream>
#include <omp.h>
#include <vector>

int main() {
    constexpr int grid_size = 1000;
    constexpr int time_steps = 100;

    std::vector<double> current(
        grid_size * grid_size, 20.0);
    std::vector<double> next = current;

    const int center = (grid_size / 2) * grid_size + (grid_size / 2);
    current[center] = 100.0;

    const auto start_time = std::chrono::steady_clock::now();

    for (int step = 0; step < time_steps; ++step) {
        #pragma omp parallel for
        for (int row = 1; row < grid_size - 1; ++row) {
            for (int col = 1; col < grid_size - 1; ++col) {
                const int index = row * grid_size + col;

                next[index] = 0.25 * (
                    current[index - grid_size] +
                    current[index + grid_size] +
                    current[index - 1] +
                    current[index + 1]);
            }
        }

        current.swap(next);
    }

    const auto end_time = std::chrono::steady_clock::now();
    const std::chrono::duration<double, std::milli> elapsed_time =
        end_time - start_time;

    std::cout << "Center temperature after " << time_steps
              << " steps: " << std::fixed << std::setprecision(2)
              << current[center] << " degrees\n";
    std::cout << "OpenMP threads: " << omp_get_max_threads() << '\n';
    std::cout << "Simulation time: " << elapsed_time.count() << " ms\n";
}