# Draft language planning tables

These are conditional forecasts, not frozen executable plans.

## B/C survivor case

Status: draft; survivors: B, C; final seeds: 1, 2, 3.
Common training FLOPs/run: 1.21406701423049e+17.

| Arm | Forward FLOPs/token | Training FLOPs/token | Main updates | Main tokens | Excess updates | Sweep timeout | Main timeout |
|---|---:|---:|---:|---:|---:|---:|---:|
| rawS | 92473464.0 | 277420392.0 | 13356 | 437649408 | 0.678609 | 500s | 1600s |
| convS | 92528760.0 | 277586280.0 | 13348 | 437387264 | 0.659866 | 600s | 1900s |
| convP | 98872512.0 | 296617536.0 | 12491 | 409305088 | 0.037579 | 600s | 2100s |
| B | 101163294.1875 | 303489882.5625 | 12209 | 400064512 | 0.887939 | 800s | 2600s |
| C | 101172510.1875 | 303517530.5625 | 12207 | 399998976 | 0.000000 | 800s | 2600s |
| GDN1 | 98067262.5 | 294429883.5 | 12584 | 412352512 | 0.228096 | 800s | 2700s |
| DP4 | 123706314.0 | 372031326.0 | 9959 | 326336512 | 0.057737 | 1600s | 4900s |

Forecast including earlier language spend: $76.24; aggregate timeout maximum: $98.36.
All arms receive three fresh 3,051-update seed-0 rate trials; finals start fresh.
Inference ablations and final losses never select rates or additional runs.

## A/B/C survivor case

Status: draft; survivors: A, B, C; final seeds: 1, 2, 3.
Common training FLOPs/run: 1.29097779333839e+17.

| Arm | Forward FLOPs/token | Training FLOPs/token | Main updates | Main tokens | Excess updates | Sweep timeout | Main timeout |
|---|---:|---:|---:|---:|---:|---:|---:|
| rawS | 92473464.0 | 277420392.0 | 14202 | 465371136 | 0.623028 | 500s | 1700s |
| convS | 92528760.0 | 277586280.0 | 14193 | 465076224 | 0.109895 | 600s | 2000s |
| convP | 98872512.0 | 296617536.0 | 13283 | 435257344 | 0.738878 | 600s | 2200s |
| A | 107581758.1875 | 322745274.5625 | 12207 | 399998976 | 0.000000 | 1000s | 3300s |
| B | 101163294.1875 | 303489882.5625 | 12982 | 425394176 | 0.507723 | 800s | 2800s |
| C | 101172510.1875 | 303517530.5625 | 12981 | 425361408 | 0.690232 | 800s | 2800s |
| GDN1 | 98067262.5 | 294429883.5 | 13381 | 438468608 | 0.049942 | 800s | 2900s |
| DP4 | 123706314.0 | 372031326.0 | 10590 | 347013120 | 0.161749 | 1600s | 5200s |

Forecast including earlier language spend: $92.15; aggregate timeout maximum: $119.61.
All arms receive three fresh 3,051-update seed-0 rate trials; finals start fresh.
Inference ablations and final losses never select rates or additional runs.
