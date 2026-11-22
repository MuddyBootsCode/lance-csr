# Issue 186 benchmark comparison

Baseline commit `c9cd09659e7deb2516b88d8c6f65ead5f2b3a9b6`. Branch build uses the same commit plus `revision.patch` (SHA-256 `237a6c41f063d6fe7a2b2fa8b5ba67d2263d6cbc18d06c14bf36c96d496b1419`).

Both release wheels were built on Apple M5 Max with 128 GiB, macOS 27.0.1, Rust 1.96.0 and the macOS 26.2 Command Line Tools SDK.

Each workload ran twice per wheel in each storage mode. Lower latency is faster. The load averages and active validation slots at the start of each run are in `machine-load.jsonl`.

## graph-benchmark-ldbc

Runner commit `199852076ba8dceb345e18eeb2f8ac04c73f3ea1`.

### memory

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 0.693 | 0.769 | 0.710 | 0.728 | -1.6% | +10.9% |
| test_benchmark_query2 | 0.653 | 0.663 | 0.687 | 0.591 | -2.9% | +1.4% |
| test_benchmark_query3 | 0.688 | 0.856 | 0.729 | 0.788 | -1.7% | +24.3% |
| test_benchmark_query4 | 0.552 | 0.605 | 0.556 | 0.623 | +1.8% | +9.6% |
| test_benchmark_query5 | 1.064 | 1.156 | 1.043 | 1.068 | -5.0% | +8.6% |
| test_benchmark_query6 | 0.489 | 0.487 | 0.481 | 0.483 | -1.3% | -0.3% |
| test_benchmark_query7 | 1.367 | 1.243 | 1.290 | 1.240 | -3.1% | -9.1% |
| test_benchmark_query8 | 0.933 | 0.840 | 0.824 | 0.843 | -6.0% | -10.0% |
| test_benchmark_query9 | 1.000 | 0.912 | 1.007 | 0.927 | +1.2% | -8.8% |
| test_benchmark_query10 | 0.909 | 0.922 | 0.901 | 0.900 | -1.7% | +1.4% |
| test_benchmark_query11 | 1.647 | 1.929 | 1.973 | 1.960 | +10.0% | +17.2% |
| test_benchmark_query12 | 0.779 | 0.865 | 1.005 | 1.078 | +26.8% | +11.1% |
| test_benchmark_query13 | 0.845 | 0.866 | 0.881 | 0.870 | +2.3% | +2.5% |
| test_benchmark_query14 | 0.610 | 0.662 | 0.602 | 0.659 | -0.9% | +8.4% |
| test_benchmark_query15 | 0.625 | 0.659 | 0.703 | 0.644 | +5.0% | +5.4% |
| test_benchmark_query16 | 0.767 | 0.806 | 0.809 | 0.838 | +4.7% | +5.1% |
| test_benchmark_query17 | 1.342 | 1.089 | 1.091 | 1.316 | -1.0% | -18.8% |
| test_benchmark_query18 | 0.783 | 0.749 | 0.750 | 0.816 | +2.2% | -4.3% |
| test_benchmark_query19 | 1.341 | 1.249 | 1.132 | 1.323 | -5.2% | -6.9% |
| test_benchmark_query20 | 1.542 | 1.700 | 1.815 | 2.024 | +18.4% | +10.3% |
| test_benchmark_query21 | 0.818 | 0.781 | 0.837 | 0.907 | +9.1% | -4.5% |
| test_benchmark_query22 | 0.818 | 0.773 | 0.928 | 0.860 | +12.4% | -5.5% |
| test_benchmark_query23 | 0.818 | 0.839 | 0.832 | 1.018 | +11.6% | +2.6% |
| test_benchmark_query24 | 0.760 | 0.818 | 0.783 | 0.776 | -1.2% | +7.6% |
| test_benchmark_query25 | 0.913 | 0.918 | 0.988 | 0.963 | +6.5% | +0.6% |
| test_benchmark_query26 | 0.918 | 0.890 | 0.850 | 0.877 | -4.5% | -3.1% |
| test_benchmark_query27 | 1.270 | 1.191 | 0.951 | 1.018 | -20.0% | -6.2% |
| test_benchmark_query28 | 1.488 | 1.762 | 1.760 | 1.762 | +8.4% | +18.4% |
| test_benchmark_query29 | 0.832 | 0.842 | 0.922 | 0.793 | +2.5% | +1.2% |
| test_benchmark_query30 | 10.074 | 12.553 | 11.056 | 11.242 | -1.5% | +24.6% |

Geometric mean of per-query branch/main ratios: 1.0184.

### lazy

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 1.387 | 1.745 | 2.456 | 1.759 | +34.6% | +25.8% |
| test_benchmark_query2 | 1.455 | 1.812 | 2.449 | 1.958 | +34.9% | +24.5% |
| test_benchmark_query3 | 1.148 | 0.943 | 1.778 | 0.960 | +30.9% | -17.9% |
| test_benchmark_query4 | 1.244 | 1.049 | 1.739 | 1.363 | +35.3% | -15.7% |
| test_benchmark_query5 | 2.345 | 2.478 | 3.384 | 2.851 | +29.3% | +5.7% |
| test_benchmark_query6 | 0.833 | 1.101 | 1.595 | 1.116 | +40.1% | +32.1% |
| test_benchmark_query7 | 1.410 | 2.400 | 2.234 | 1.823 | +6.5% | +70.2% |
| test_benchmark_query8 | 1.970 | 2.956 | 2.488 | 1.968 | -9.5% | +50.0% |
| test_benchmark_query9 | 1.523 | 2.284 | 2.453 | 1.767 | +10.9% | +49.9% |
| test_benchmark_query10 | 1.231 | 1.780 | 1.988 | 1.482 | +15.3% | +44.6% |
| test_benchmark_query11 | 2.339 | 3.686 | 2.880 | 2.640 | -8.4% | +57.6% |
| test_benchmark_query12 | 5.092 | 6.604 | 5.330 | 5.459 | -7.7% | +29.7% |
| test_benchmark_query13 | 1.514 | 2.244 | 1.873 | 1.679 | -5.5% | +48.2% |
| test_benchmark_query14 | 0.815 | 1.590 | 1.094 | 1.164 | -6.1% | +95.1% |
| test_benchmark_query15 | 1.409 | 1.832 | 1.577 | 1.332 | -10.2% | +30.0% |
| test_benchmark_query16 | 1.768 | 2.102 | 1.613 | 1.586 | -17.3% | +18.9% |
| test_benchmark_query17 | 2.903 | 3.281 | 2.951 | 2.791 | -7.2% | +13.0% |
| test_benchmark_query18 | 2.408 | 2.506 | 2.104 | 2.600 | -4.3% | +4.1% |
| test_benchmark_query19 | 3.298 | 2.289 | 2.225 | 2.833 | -9.5% | -30.6% |
| test_benchmark_query20 | 47.648 | 43.011 | 46.411 | 53.659 | +10.4% | -9.7% |
| test_benchmark_query21 | 1.645 | 1.761 | 1.109 | 1.290 | -29.6% | +7.1% |
| test_benchmark_query22 | 1.926 | 1.991 | 1.431 | 1.991 | -12.7% | +3.4% |
| test_benchmark_query23 | 2.321 | 2.025 | 1.861 | 2.094 | -9.0% | -12.7% |
| test_benchmark_query24 | 2.160 | 1.676 | 1.897 | 1.744 | -5.1% | -22.4% |
| test_benchmark_query25 | 2.422 | 1.744 | 2.180 | 2.066 | +1.9% | -28.0% |
| test_benchmark_query26 | 2.146 | 1.553 | 1.719 | 2.712 | +19.8% | -27.6% |
| test_benchmark_query27 | 2.860 | 2.063 | 1.819 | 2.906 | -4.0% | -27.9% |
| test_benchmark_query28 | 4.009 | 3.125 | 2.600 | 3.218 | -18.5% | -22.1% |
| test_benchmark_query29 | 2.274 | 2.155 | 1.664 | 2.309 | -10.3% | -5.2% |
| test_benchmark_query30 | 18.942 | 14.195 | 13.271 | 15.705 | -12.6% | -25.1% |

Geometric mean of per-query branch/main ratios: 1.0115.

## graph-benchmark-ldbc-complex

Runner commit `a332324f2d4660b03d1d429d8ef99767af3981e5`.

### memory

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 26.778 | 23.800 | 24.202 | 23.079 | -6.5% | -11.1% |
| test_benchmark_query2 | 3.725 | 2.958 | 2.766 | 2.609 | -19.6% | -20.6% |
| test_benchmark_query3 | 23.563 | 26.167 | 21.421 | 22.179 | -12.3% | +11.1% |
| test_benchmark_query4 | 6.941 | 6.340 | 6.340 | 6.544 | -3.0% | -8.7% |
| test_benchmark_query5 | 43.739 | 41.478 | 49.675 | 40.899 | +6.3% | -5.2% |
| test_benchmark_query6 | 26.965 | 22.459 | 26.639 | 22.976 | +0.4% | -16.7% |
| test_benchmark_query7 | 11.405 | 9.470 | 10.859 | 9.343 | -3.2% | -17.0% |
| test_benchmark_query8 | 2.680 | 2.569 | 2.573 | 2.377 | -5.7% | -4.2% |
| test_benchmark_query9 | 42.022 | 45.221 | 41.601 | 35.478 | -11.6% | +7.6% |
| test_benchmark_query10 | 16.299 | 15.942 | 15.936 | 14.198 | -6.5% | -2.2% |
| test_benchmark_query11 | 3.613 | 3.761 | 3.627 | 3.002 | -10.1% | +4.1% |
| test_benchmark_query12 | 17.549 | 21.754 | 16.649 | 14.923 | -19.7% | +24.0% |
| test_benchmark_query13 | 1.183 | 1.133 | 1.357 | 1.428 | +20.2% | -4.2% |
| test_benchmark_query14 | 274.899 | 254.386 | 294.588 | 269.365 | +6.6% | -7.5% |

Geometric mean of per-query branch/main ratios: 0.9483.

### lazy

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 37.201 | 34.703 | 35.476 | 38.463 | +2.8% | -6.7% |
| test_benchmark_query2 | 26.659 | 25.366 | 24.938 | 27.587 | +1.0% | -4.8% |
| test_benchmark_query3 | 161.758 | 163.896 | 161.952 | 172.416 | +2.7% | +1.3% |
| test_benchmark_query4 | 13.950 | 14.010 | 13.774 | 14.613 | +1.5% | +0.4% |
| test_benchmark_query5 | 73.344 | 83.841 | 74.129 | 76.894 | -3.9% | +14.3% |
| test_benchmark_query6 | 23.839 | 33.948 | 22.048 | 29.129 | -11.4% | +42.4% |
| test_benchmark_query7 | 14.211 | 15.555 | 13.680 | 13.758 | -7.8% | +9.5% |
| test_benchmark_query8 | 4.031 | 3.548 | 3.427 | 3.741 | -5.4% | -12.0% |
| test_benchmark_query9 | 205.173 | 212.381 | 213.228 | 218.859 | +3.5% | +3.5% |
| test_benchmark_query10 | 22.963 | 25.110 | 22.750 | 23.924 | -2.9% | +9.3% |
| test_benchmark_query11 | 5.680 | 8.069 | 5.764 | 6.331 | -12.0% | +42.1% |
| test_benchmark_query12 | 19.688 | 22.786 | 17.413 | 21.190 | -9.1% | +15.7% |
| test_benchmark_query13 | 1.485 | 1.631 | 1.414 | 1.443 | -8.3% | +9.8% |
| test_benchmark_query14 | 282.588 | 318.989 | 258.264 | 292.301 | -8.5% | +12.9% |

Geometric mean of per-query branch/main ratios: 0.9571.
