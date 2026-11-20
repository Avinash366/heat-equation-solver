#include <algorithm>
#include <chrono>
#include <condition_variable>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

#include "common.hpp"

// Reusable barrier (C++17 has no std::barrier). Every worker waits here
// until all workers have finished the current time step.
class Barrier {
public:
    explicit Barrier(int count) : count_(count) {}

    void arrive_and_wait() {
        std::unique_lock<std::mutex> lock(mutex_);
        const unsigned long generation = generation_;
        if (++waiting_ == count_) {
            waiting_ = 0;
            ++generation_;
            condition_.notify_all();
        } else {
            condition_.wait(lock, [&] { return generation != generation_; });
        }
    }

private:
    std::mutex mutex_;
    std::condition_variable condition_;
    const int count_;
    int waiting_ = 0;
    unsigned long generation_ = 0;
};

int main(int argc, char* argv[]) {
    const Settings settings = parse_settings(argc, argv);
    const int grid_size = settings.grid_size;
    const int time_steps = settings.time_steps;

    // Two buffers; step N reads grids[N % 2] and writes grids[(N + 1) % 2].
    std::vector<std::vector<double>> grids[2] = {
        std::vector<std::vector<double>>(
            grid_size, std::vector<double>(grid_size, 20.0)),
        {}};
    grids[0][grid_size / 2][grid_size / 2] = 100.0;
    grids[1] = grids[0];

    const unsigned int available_threads = std::thread::hardware_concurrency();
    const int requested_threads = settings.threads > 0
        ? settings.threads
        : static_cast<int>(available_threads == 0 ? 1 : available_threads);
    const int interior_rows = grid_size - 2;
    const int thread_count = std::min(requested_threads, interior_rows);

    Barrier barrier(thread_count);

    const auto start_time = std::chrono::steady_clock::now();

    // Threads are created once and reused for every time step.
    std::vector<std::thread> workers;
    for (int thread_id = 0; thread_id < thread_count; ++thread_id) {
        const int first_row = 1 + (interior_rows * thread_id) / thread_count;
        const int past_last_row =
            1 + (interior_rows * (thread_id + 1)) / thread_count;

        workers.emplace_back([&, first_row, past_last_row]() {
            for (int step = 0; step < time_steps; ++step) {
                const auto& current = grids[step % 2];
                auto& next = grids[(step + 1) % 2];

                for (int row = first_row; row < past_last_row; ++row) {
                    for (int col = 1; col < grid_size - 1; ++col) {
                        next[row][col] = 0.25 * (
                            current[row - 1][col] + current[row + 1][col] +
                            current[row][col - 1] + current[row][col + 1]);
                    }
                }

                // No thread starts the next step until all rows are done.
                barrier.arrive_and_wait();
            }
        });
    }

    for (std::thread& worker : workers) {
        worker.join();
    }

    const auto end_time = std::chrono::steady_clock::now();
    const std::chrono::duration<double, std::milli> elapsed_time =
        end_time - start_time;

    const auto& current = grids[time_steps % 2];

    // Save the final temperature grid for the visualization.
    std::ofstream output_file("heat_output.csv");

    if (!output_file) {
        std::cerr << "Could not create heat_output.csv\n";
        return 1;
    }

    double checksum = 0.0;
    for (int row = 0; row < grid_size; ++row) {
        for (int col = 0; col < grid_size; ++col) {
            if (col > 0) {
                output_file << ",";
            }
            output_file << current[row][col];
            checksum += current[row][col];
        }
        output_file << "\n";
    }

    output_file.close();

    std::cout << "Grid: " << grid_size << " x " << grid_size
              << ", steps: " << time_steps << '\n';
    std::cout << "Center temperature after " << time_steps
              << " steps: " << std::fixed << std::setprecision(2)
              << current[grid_size / 2][grid_size / 2] << " degrees\n";
    std::cout << "Grid checksum: " << std::setprecision(6) << checksum << '\n';
    std::cout << "C++ threads: " << thread_count << '\n';
    std::cout << "Simulation time: " << std::setprecision(2)
              << elapsed_time.count() << " ms\n";
}
