#include <chrono>
#include <iomanip>
#include <iostream>
#include <omp.h>
#include <vector>

#include "common.hpp"

// Same algorithm as heat_openmp.cpp, but the grid is stored as one flat,
// contiguous array instead of a vector of row vectors. This removes the
// per-row pointer lookup and keeps neighboring rows next to each other
// in memory.
int main(int argc, char* argv[]) {
    const Settings settings = parse_settings(argc, argv);
    const int grid_size = settings.grid_size;
    const int time_steps = settings.time_steps;
    if (settings.threads > 0) {
        omp_set_num_threads(settings.threads);  // overrides OMP_NUM_THREADS
    }

    const std::size_t cell_count =
        static_cast<std::size_t>(grid_size) * grid_size;
    std::vector<double> current(cell_count, 20.0);
    std::vector<double> next = current;

    const std::size_t center =
        static_cast<std::size_t>(grid_size / 2) * grid_size + grid_size / 2;
    current[center] = 100.0;

    const auto start_time = std::chrono::steady_clock::now();

    for (int step = 0; step < time_steps; ++step) {
        #pragma omp parallel for schedule(static)
        for (int row = 1; row < grid_size - 1; ++row) {
            const double* above = &current[static_cast<std::size_t>(row - 1) * grid_size];
            const double* here = above + grid_size;
            const double* below = here + grid_size;
            double* out = &next[static_cast<std::size_t>(row) * grid_size];

            for (int col = 1; col < grid_size - 1; ++col) {
                out[col] = 0.25 * (
                    above[col] + below[col] + here[col - 1] + here[col + 1]);
            }
        }

        current.swap(next);
    }

    const auto end_time = std::chrono::steady_clock::now();
    const std::chrono::duration<double, std::milli> elapsed_time =
        end_time - start_time;

    double checksum = 0.0;
    for (double value : current) {
        checksum += value;
    }

    std::cout << "Grid: " << grid_size << " x " << grid_size
              << ", steps: " << time_steps << '\n';
    std::cout << "Center temperature after " << time_steps
              << " steps: " << std::fixed << std::setprecision(2)
              << current[center] << " degrees\n";
    std::cout << "Grid checksum: " << std::setprecision(6) << checksum << '\n';
    std::cout << "OpenMP threads: " << omp_get_max_threads() << '\n';
    std::cout << "Simulation time: " << std::setprecision(2)
              << elapsed_time.count() << " ms\n";
}
