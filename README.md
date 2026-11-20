# Parallel Heat Diffusion Solver

ECE 6360 project comparing sequential and CPU-parallel ways to simulate heat spreading across a two-dimensional plate.

## Numerical model

The default grid is 1000 × 1000. Every cell starts at 20 degrees, except the center cell, which starts at 100 degrees. The outer edge remains fixed at 20 degrees. The simulation runs for 100 time steps.

At each step, every interior cell is updated from its four neighbors in the previous step:

```text
T_next[row][col] = 0.25 × (above + below + left + right)
```

The program keeps separate `current` and `next` grids. It reads only from `current`, writes the new temperatures to `next`, and swaps the grids after all cells have been updated. This is a five-point finite-difference stencil. The averaging formula corresponds to the two-dimensional explicit heat equation with equal grid spacing and diffusion factor `alpha × time_step / spacing² = 0.25`.

## Implementations

- `src/heat_sequential.cpp` updates the grid on one CPU thread.
- `src/heat_openmp.cpp` uses OpenMP to divide grid rows among CPU threads.
- `src/heat_threads.cpp` uses `std::thread` and manually divides rows among worker threads. The workers are created once and synchronized with a barrier after each time step. It also writes the final grid to `heat_output.csv`.
- `src/heat_optimized.cpp` uses OpenMP with the grid stored as one flat, contiguous array instead of a vector of row vectors, which removes the per-row pointer lookup.
- `src/common.hpp` reads the shared command-line settings.

All versions use the same temperature update. The flat-array version changes the memory layout, and the parallel versions change how rows are assigned to CPU threads. Every program prints a grid checksum (the sum of all cells), so you can confirm that all versions produce the same final grid.

## Build and run on Windows

Requirements: CMake, the MSYS2 MinGW GCC compiler, and Python with Matplotlib for generating the visualizations.

Open PowerShell in this project folder and configure the build. CMake defaults to an optimized Release build:

```powershell
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

Each program takes optional arguments: `[grid_size] [time_steps] [threads]`. The defaults are a 1000 × 1000 grid and 100 steps. If no thread count is given, OpenMP uses `OMP_NUM_THREADS` and the C++ Threads version uses `std::thread::hardware_concurrency()`.

```powershell
.\build\heat_sequential.exe 1000 100
.\build\heat_openmp.exe 1000 100 8
.\build\heat_threads.exe 1000 100 8
.\build\heat_optimized.exe 1000 100 8
```

To benchmark every version on 500, 1000 and 1500 grids (three runs each) and save the averages and checksums to `release_benchmarks.csv`:

```powershell
.\run_benchmarks.ps1
```

## Visualizations

Run `heat_threads.exe` to create `heat_output.csv`, then create the heatmap with:

```powershell
python visualize.py
```

The script saves `heatmap.png`. After running `run_benchmarks.ps1`, generate charts from its results with `python benchmark_plot.py` (all grid sizes) and `python release_benchmark_plot.py` (1000 × 1000 comparison).

## Release benchmark results

These measurements were collected on the project computer using a Release build, a 1000 × 1000 grid, 100 time steps, and three runs per version. Parallel versions used 8 threads. All versions produced a center temperature of 20.51 degrees and the same grid checksum, 20000080.

| Version | Average runtime | Speedup over sequential |
|---|---:|---:|
| Sequential | 95.42 ms | 1.00× |
| OpenMP | 78.16 ms | 1.22× |
| Persistent C++ threads | 63.40 ms | 1.50× |
| Flat-array OpenMP | 65.04 ms | 1.47× |

The persistent C++ threads version was fastest in this Release comparison. Reusing workers across steps improved its result compared with the earlier implementation, which created and joined workers at every step. The flat-array OpenMP version was close behind. Runtime varies by computer and system load, so use the measurements in `release_benchmarks.csv` as the source for the included charts.

The same benchmark run recorded the following averages for all tested sizes:

| Grid size | Sequential | OpenMP (8) | Persistent C++ threads (8) | Flat-array OpenMP (8) |
|---|---:|---:|---:|---:|
| 500 × 500 | 20.14 ms | 20.61 ms | 23.31 ms | 22.66 ms |
| 1000 × 1000 | 95.42 ms | 78.16 ms | 63.40 ms | 65.04 ms |
| 1500 × 1500 | 246.94 ms | 128.92 ms | 101.64 ms | 83.16 ms |

At 500 × 500, the sequential version was fastest, as thread overhead is significant for a smaller workload. At 1000 × 1000, persistent C++ threads were fastest. At 1500 × 1500, the flat-array OpenMP version was fastest. All sizes produced matching checksums across the four solvers: 5000080, 20000080, and 45000080, respectively.

## CUDA

CUDA was optional in the proposal. It is not included because this computer has an Intel Arc 130V GPU rather than a CUDA-capable NVIDIA GPU.

## Presentation

The project presentation is saved at deliverables/heat_diffusion_project_presentation.pptx.
