#pragma once

#include <cstdlib>
#include <iostream>
#include <string>

// Command-line settings shared by every solver:
//   program [grid_size] [time_steps] [threads]
// Missing values fall back to the defaults below.
struct Settings {
    int grid_size = 1000;
    int time_steps = 100;
    int threads = 0;  // 0 = let the program choose
};

inline Settings parse_settings(int argc, char* argv[]) {
    Settings settings;
    try {
        if (argc > 1) settings.grid_size = std::stoi(argv[1]);
        if (argc > 2) settings.time_steps = std::stoi(argv[2]);
        if (argc > 3) settings.threads = std::stoi(argv[3]);
    } catch (const std::exception&) {
        std::cerr << "Usage: " << argv[0] << " [grid_size] [time_steps] [threads]\n";
        std::exit(1);
    }
    if (settings.grid_size < 3 || settings.time_steps < 0 || settings.threads < 0) {
        std::cerr << "grid_size must be at least 3; time_steps and threads must not be negative\n";
        std::exit(1);
    }
    return settings;
}
