# Runs every solver on several grid sizes, three times each, and saves
# the average times to release_benchmarks.csv.
# Usage (from the project folder, after building in Release):
#   .\run_benchmarks.ps1
#   .\run_benchmarks.ps1 -Threads 4 -Runs 5

param(
    [int[]]$GridSizes = @(500, 1000, 1500),
    [int]$Steps = 100,
    [int]$Threads = 8,
    [int]$Runs = 3
)

$versions = @("heat_sequential", "heat_openmp", "heat_threads", "heat_optimized")
$results = @()

foreach ($grid in $GridSizes) {
    foreach ($version in $versions) {
        $exe = Join-Path $PSScriptRoot "build\$version.exe"
        $times = @()
        $checksum = ""
        for ($run = 1; $run -le $Runs; $run++) {
            $output = & $exe $grid $Steps $Threads
            $timeLine = $output | Select-String "Simulation time: ([\d.]+) ms"
            $times += [double]$timeLine.Matches[0].Groups[1].Value
            $checksum = ($output | Select-String "Grid checksum: ([\d.]+)").Matches[0].Groups[1].Value
        }
        $average = ($times | Measure-Object -Average).Average
        Write-Host ("{0,-16} grid {1,5}: {2,9:N2} ms  (checksum {3})" -f $version, $grid, $average, $checksum)
        $results += [pscustomobject]@{
            version = $version
            grid_size = $grid
            steps = $Steps
            threads = $(if ($version -eq "heat_sequential") { 1 } else { $Threads })
            average_ms = [math]::Round($average, 2)
            checksum = $checksum
        }
    }
}

$results | Export-Csv (Join-Path $PSScriptRoot "release_benchmarks.csv") -NoTypeInformation
Write-Host "Saved release_benchmarks.csv"
