# Draft language planning tables

These are conditional forecasts under the prospective conservative control allowance, not frozen executable plans. Original worker FLOP counters and candidate schedules are unchanged.

## B+C survivor case

Status: draft; survivors: B, C; final seeds: 1, 2, 3.
Nominal candidate reference budget: 1.21406701423049e+17 training FLOPs/run.
Controls receive the smallest whole-update allowance covering every candidate under all four declared arithmetic conventions.
Allowance policy: `3a340829e3fa07d6808280c240992af63283088ac92a3d68d7935cb7822d0991`.

| Arm | Nominal forward/token | Nominal training/token | Nominal + remat | Source upper | Source upper + remat |
|---|---:|---:|---:|---:|---:|
| rawS | 92473464.0 | 277420392.0 | 318382560.0 | 287023104.0 | 331186176.0 |
| convS | 92528760.0 | 277586280.0 | 318603744.0 | 287188992.0 | 331407360.0 |
| convP | 98872512.0 | 296617536.0 | 343978752.0 | 306312192.0 | 356904960.0 |
| B | 101163294.1875 | 303489882.5625 | 353141880.75 | 313184538.5625 | 366068088.75 |
| C | 101172510.1875 | 303517530.5625 | 353178744.75 | 313212186.5625 | 366104952.75 |
| GDN1 | 98067262.5 | 294429883.5 | 340985850.0 | 294429883.5 | 340985850.0 |
| DP4 | 123706314.0 | 372031326.0 | 444226344.0 | 372031326.0 | 444226344.0 |

| Arm | Original nominal updates | Added control updates | Final updates | Final tokens | Binding requirement | Rounding excess | Sweep/final timeout |
|---|---:|---:|---:|---:|---|---:|---:|
| rawS | 13356 | 186 | 13542 | 443744256 | B / nominal_remat | 0.086077 | 500s / 1600s |
| convS | 13348 | 185 | 13533 | 443449344 | B / nominal_remat | 0.487268 | 600s / 1900s |
| convP | 12491 | 44 | 12535 | 410746880 | B / nominal_remat | 0.768752 | 600s / 2100s |
| B | 12209 | 0 | 12209 | 400064512 | fixed candidate schedule | 0.887939 | 800s / 2600s |
| C | 12207 | 0 | 12207 | 399998976 | fixed candidate schedule | 0.000000 | 800s / 2600s |
| GDN1 | 12584 | 524 | 13108 | 429522944 | B / source_upper_remat | 0.930321 | 800s / 2900s |
| DP4 | 9959 | 319 | 10278 | 336789504 | B / source_upper | 0.182612 | 1600s / 5100s |

Forecast including earlier language spend: $77.09; aggregate timeout maximum: $99.82.
The control allowance adds $0.85 forecast and $1.46 aggregate timeout reservations.
All arms receive three fresh 3,051-update seed-0 rate trials; finals start fresh.
Inference ablations and final losses never select rates or additional runs.
These are conservative declared arithmetic estimates, not equal measured GPU-executed FLOPs.

## A+B+C survivor case

Status: draft; survivors: A, B, C; final seeds: 1, 2, 3.
Nominal candidate reference budget: 1.29097779333839e+17 training FLOPs/run.
Controls receive the smallest whole-update allowance covering every candidate under all four declared arithmetic conventions.
Allowance policy: `3a340829e3fa07d6808280c240992af63283088ac92a3d68d7935cb7822d0991`.

| Arm | Nominal forward/token | Nominal training/token | Nominal + remat | Source upper | Source upper + remat |
|---|---:|---:|---:|---:|---:|
| rawS | 92473464.0 | 277420392.0 | 318382560.0 | 287023104.0 | 331186176.0 |
| convS | 92528760.0 | 277586280.0 | 318603744.0 | 287188992.0 | 331407360.0 |
| convP | 98872512.0 | 296617536.0 | 343978752.0 | 306312192.0 | 356904960.0 |
| A | 107581758.1875 | 322745274.5625 | 378815736.75 | 341858394.5625 | 404299896.75 |
| B | 101163294.1875 | 303489882.5625 | 353141880.75 | 313184538.5625 | 366068088.75 |
| C | 101172510.1875 | 303517530.5625 | 353178744.75 | 313212186.5625 | 366104952.75 |
| GDN1 | 98067262.5 | 294429883.5 | 340985850.0 | 294429883.5 | 340985850.0 |
| DP4 | 123706314.0 | 372031326.0 | 444226344.0 | 372031326.0 | 444226344.0 |

| Arm | Original nominal updates | Added control updates | Final updates | Final tokens | Binding requirement | Rounding excess | Sweep/final timeout |
|---|---:|---:|---:|---:|---|---:|---:|
| rawS | 14202 | 700 | 14902 | 488308736 | A / source_upper_remat | 0.143590 | 500s / 1800s |
| convS | 14193 | 699 | 14892 | 487981056 | A / source_upper_remat | 0.089212 | 600s / 2000s |
| convP | 13283 | 546 | 13829 | 453148672 | A / source_upper_remat | 0.980239 | 600s / 2300s |
| A | 12207 | 0 | 12207 | 399998976 | fixed candidate schedule | 0.000000 | 1000s / 3300s |
| B | 12982 | 0 | 12982 | 425394176 | fixed candidate schedule | 0.507723 | 800s / 2800s |
| C | 12981 | 0 | 12981 | 425361408 | fixed candidate schedule | 0.690232 | 800s / 2800s |
| GDN1 | 13381 | 1093 | 14474 | 474284032 | A / source_upper_remat | 0.411610 | 800s / 3100s |
| DP4 | 10590 | 627 | 11217 | 367558656 | A / source_upper | 0.026775 | 1600s / 5500s |

Forecast including earlier language spend: $94.26; aggregate timeout maximum: $122.17.
The control allowance adds $2.12 forecast and $2.56 aggregate timeout reservations.
All arms receive three fresh 3,051-update seed-0 rate trials; finals start fresh.
Inference ablations and final losses never select rates or additional runs.
These are conservative declared arithmetic estimates, not equal measured GPU-executed FLOPs.
