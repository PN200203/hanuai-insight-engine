> WARNING: SYNTHETIC demo data - illustrates the format only.

Rows after cleaning: **1202** (raw 1230). Clusters: **k=9** (silhouette 0.25).

**Top issue categories**
| issue_category              |   count |
|:----------------------------|--------:|
| Electrical / Short & Power  |     271 |
| Energy Storage (Battery)    |     173 |
| Mechanical Wear / Vibration |     173 |
| Thermal / Overheating       |     171 |
| Leakage / Fluid System      |     156 |

**Top components**
| primary_component   |   count |
|:--------------------|--------:|
| battery pack        |     301 |
| control board       |     149 |
| motor               |     113 |
| sensor              |     102 |
| pump                |      99 |

**Strongest root-cause candidates (lift)**
| driver            | driver_value                   | outcome                   |   count |   lift |     p_value |       p_adj | actionable   |
|:------------------|:-------------------------------|:--------------------------|--------:|-------:|------------:|------------:|:-------------|
| product_model     | Rx-300                         | Energy Storage (Battery)  |     115 |   1.92 | 2.42734e-20 | 2.37879e-18 | True         |
| product_model     | Rx-300                         | battery pack              |     191 |   1.86 | 1.72309e-34 | 2.15386e-32 | True         |
| primary_condition | under full load                | pump                      |      28 |   1.63 | 0.00315028  | 0.393785    | False        |
| primary_condition | after 3 months in service      | Uncategorised             |       9 |   1.62 | 0.0860704   | 1           | False        |
| product_model     | Rx-200                         | Corrosion / Environmental |      16 |   1.55 | 0.017345    | 1           | False        |
| primary_condition | after 3 months in service      | motor                     |      32 |   1.53 | 0.00492946  | 0.616182    | False        |
| region            | North                          | Display / UI              |      26 |   1.51 | 0.00750886  | 0.735868    | False        |
| primary_condition | after vibration on rough roads | bearing                   |      22 |   1.49 | 0.0267019   | 1           | False        |

**Recent 3-month change by category**
| issue_category              |   prev_3m |   last_3m |   change_% |
|:----------------------------|----------:|----------:|-----------:|
| Leakage / Fluid System      |        18 |        24 |       33.3 |
| Uncategorised               |         6 |         7 |       16.7 |
| Electrical / Short & Power  |        36 |        39 |        8.3 |
| Thermal / Overheating       |        28 |        29 |        3.6 |
| Mechanical Wear / Vibration |        25 |        24 |       -4   |
| Display / UI                |         4 |         3 |      -25   |
| Energy Storage (Battery)    |        13 |         9 |      -30.8 |
| Sensor / Calibration        |        23 |        12 |      -47.8 |
| Corrosion / Environmental   |         4 |         2 |      -50   |

**downtime_hours by issue category (mean)**
| issue_category              |   downtime_hours |
|:----------------------------|-----------------:|
| Energy Storage (Battery)    |              6.8 |
| Uncategorised               |              6.5 |
| Thermal / Overheating       |              6.4 |
| Electrical / Short & Power  |              6.4 |
| Sensor / Calibration        |              6.3 |
| Corrosion / Environmental   |              6.2 |
| Leakage / Fluid System      |              6.1 |
| Mechanical Wear / Vibration |              6.1 |
| Display / UI                |              6   |

**repair_cost by issue category (mean)**
| issue_category              |   repair_cost |
|:----------------------------|--------------:|
| Display / UI                |         205   |
| Sensor / Calibration        |         204   |
| Energy Storage (Battery)    |         196.4 |
| Electrical / Short & Power  |         192.6 |
| Corrosion / Environmental   |         190   |
| Mechanical Wear / Vibration |         182.4 |
| Leakage / Fluid System      |         181   |
| Thermal / Overheating       |         180.8 |
| Uncategorised               |         173.7 |