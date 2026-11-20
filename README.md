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
- `src/heat_threads.cpp` uses `std::thread` and manually divides rows among worker threads. It creates and joins workers at each time step. It also writes the final grid to `heat_output.csv`.
- `src/heat_optimized.cpp` uses OpenMP with one contiguous grid array to improve memory access.

All versions use the same temperature update. The cache-aware version changes the memory layout, and the parallel versions change how rows are assigned to CPU threads.

## Build and run on Windows

Requirements: CMake, the MSYS2 MinGW GCC compiler, and Python with Matplotlib for generating the visualizations.

Open PowerShell in this project folder and configure an optimized Release build:

```powershell
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

Run each implementation:

```powershell
.\build\heat_sequential.exe
$env:OMP_NUM_THREADS = "8"
.\build\heat_openmp.exe
.\build\heat_threads.exe
.\build\heat_optimized.exe
```

`OMP_NUM_THREADS` sets the thread count for the OpenMP programs. The C++ Threads program chooses a count using `std::thread::hardware_concurrency()`.

## Visualizations

Run `heat_threads.exe` to create `heat_output.csv`, then create the heatmap with:

```powershell
python visualize.py
```

The script saves `heatmap.png`. The preliminary multi-grid performance chart is generated with `python benchmark_plot.py`. The Release comparison chart is generated with `python release_benchmark_plot.py`.

## Release benchmark results

These measurements use a 1000 × 1000 grid, 100 time steps, and three runs per version. The parallel implementations used 8 threads. All versions produced a center temperature of 20.51 degrees.

| Version | Average runtime | Speedup over sequential |
|---|---:|---:|
| Sequential | 106.13 ms | 1.00× |
| OpenMP | 70.23 ms | 1.51× |
| C++ Threads | 145.78 ms | 0.73× |
| Cache-aware OpenMP | 65.44 ms | 1.62× |

The cache-aware OpenMP version was fastest in this Release comparison, about 7% faster than the original OpenMP version. The C++ Threads version was slower than the sequential version in this run; starting and joining workers at each time step adds overhead.

The project also includes preliminary comparisons across 500 × 500, 1000 × 1000, and 1500 × 1500 grids. Those results came from the earlier default, non-Release build, so they are kept separate from the Release results above.

## CUDA

CUDA was optional in the proposal. It is not included because this computer has an Intel Arc 130V GPU rather than a CUDA-capable NVIDIA GPU.

## Presentation

The project presentation is saved at deliverables/heat_diffusion_project_presentation.pptx.

