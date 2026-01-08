
### Column Overview

| Column Name | Data Type |
|---|---|
| feedback_id | int64 |
| user | object |
| feedback | object |
| timestamp | datetime64[ns] |


### Summary Statistics

| index       |   count |   unique | top       |   freq | mean                          | min                        | 25%                           | 50%                           | 75%                           | max                        |   std |
|:------------|--------:|---------:|:----------|-------:|:------------------------------|:---------------------------|:------------------------------|:------------------------------|:------------------------------|:---------------------------|------:|
| feedback_id |       3 |      nan | nan       |    nan | 2.0                           | 1.0                        | 1.5                           | 2.0                           | 2.5                           | 3.0                        |     1 |
| user        |       3 |        1 | anonymous |      3 | nan                           | nan                        | nan                           | nan                           | nan                           | nan                        |   nan |
| feedback    |       3 |        3 | Test1     |      1 | nan                           | nan                        | nan                           | nan                           | nan                           | nan                        |   nan |
| timestamp   |       3 |      nan | nan       |    nan | 2025-06-09 21:06:22.201649408 | 2025-06-09 12:22:24.208032 | 2025-06-09 12:41:14.968205056 | 2025-06-09 13:00:05.728378112 | 2025-06-10 01:28:21.198458112 | 2025-06-10 13:56:36.668538 |   nan |

### Categorical Distributions


**user**

| Count     |   count |
|:----------|--------:|
| anonymous |       3 |

**feedback**

| Count                                                             |   count |
|:------------------------------------------------------------------|--------:|
| Test1                                                             |       1 |
| The application is amazing! I will use it to help me from now on. |       1 |
| Testing on the feedback widget                                    |       1 |


### Correlations

| feedback_id |
|---|
| 1.0 |

### Timestamps

- **timestamp** ranges from `2025-06-09 12:22:24.208032` to `2025-06-10 13:56:36.668538`.

**Entries per day:**

| Count      |   count |
|:-----------|--------:|
| 2025-06-09 |       2 |
| 2025-06-10 |       1 |
