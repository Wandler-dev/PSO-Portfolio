# UCI 数据集画像

- 生成时间：2026-05-24T15:43:14
- 规范目标文件：`data/raw/uci_stock_portfolio_performance.xlsx`
- 实际读取文件：`data/raw/stock portfolio performance data set.xlsx`
- 文件状态：已找到
- openpyxl：可用，版本 `3.1.5`
- sheet 数量：6

## Sheet 列表

- `4th period`
- `3rd period`
- `2nd period`
- `1st period`
- `all period`
- `Time frame`

## expected_returns / covariance_matrix 初步判断

- 初步判断：当前 sheet 未呈现可直接计算协方差矩阵的宽表数值结构。
- 后续需要先完成字段解释、数值转换和表结构整理。
- 注意：4th period, 3rd period, 2nd period, 1st period, all period, Time frame 存在非数值字段，计算前必须明确保留或剔除规则。

## Sheet: 4th period

- 行数：64
- 列数：19
- 列名：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

### 每列 dtype

| column | value |
| --- | --- |
| `Unnamed: 0` | `object` |
| `the weight of the stock-picking concept` | `object` |
| `Unnamed: 2` | `object` |
| `Unnamed: 3` | `object` |
| `Unnamed: 4` | `object` |
| `Unnamed: 5` | `object` |
| `Unnamed: 6` | `object` |
| `the original investment performance indicator` | `object` |
| `Unnamed: 8` | `object` |
| `Unnamed: 9` | `object` |
| `Unnamed: 10` | `object` |
| `Unnamed: 11` | `object` |
| `Unnamed: 12` | `object` |
| `the normalized  investment performance indicator` | `object` |
| `Unnamed: 14` | `object` |
| `Unnamed: 15` | `object` |
| `Unnamed: 16` | `object` |
| `Unnamed: 17` | `object` |
| `Unnamed: 18` | `object` |

### 每列缺失值数量

| column | value |
| --- | --- |
| `Unnamed: 0` | `0` |
| `the weight of the stock-picking concept` | `0` |
| `Unnamed: 2` | `0` |
| `Unnamed: 3` | `0` |
| `Unnamed: 4` | `0` |
| `Unnamed: 5` | `0` |
| `Unnamed: 6` | `0` |
| `the original investment performance indicator` | `0` |
| `Unnamed: 8` | `0` |
| `Unnamed: 9` | `0` |
| `Unnamed: 10` | `0` |
| `Unnamed: 11` | `0` |
| `Unnamed: 12` | `0` |
| `the normalized  investment performance indicator` | `0` |
| `Unnamed: 14` | `0` |
| `Unnamed: 15` | `0` |
| `Unnamed: 16` | `0` |
| `Unnamed: 17` | `0` |
| `Unnamed: 18` | `0` |

### 前 5 行样例

```text
Unnamed: 0 the weight of the stock-picking concept  Unnamed: 2  Unnamed: 3                              Unnamed: 4           Unnamed: 5             Unnamed: 6 the original investment performance indicator    Unnamed: 8      Unnamed: 9 Unnamed: 10   Unnamed: 11   Unnamed: 12 the normalized  investment performance indicator   Unnamed: 14     Unnamed: 15 Unnamed: 16   Unnamed: 17   Unnamed: 18
        ID                              Large B/P   Large ROE   Large S/P   Large Return Rate in the last quarter   Large Market Value   Small systematic Risk                                 Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate                                    Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate
         1                                       1           0           0                                       0                    0                      0                                      0.019516      0.013399        1.902608    0.218617           0.6           0.4                                         0.488229      0.609445        0.780756         0.8          0.68      0.333333
         2                                       0           1           0                                       0                    0                      0                                      0.023829       0.00641        1.263287     0.12874          0.55          0.65                                         0.505279      0.508169        0.443776     0.41422          0.56      0.666667
         3                                       0           0           1                                       0                    0                      0                                      0.080282      0.026548        1.894339    0.208272          0.55           0.5                                         0.728484           0.8        0.776397    0.755594          0.56      0.466667
         4                                       0           0           0                                       1                    0                      0                                     -0.006683      0.000728        1.425454    0.155526          0.55          0.35                                          0.38464      0.425836        0.529253    0.529196          0.56      0.266667
```

### 带 % 的字符串

- 是否出现：否
- 出现列：
- none

### 非数值字段

- 是否存在：是
- 字段：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

## Sheet: 3rd period

- 行数：64
- 列数：19
- 列名：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

### 每列 dtype

| column | value |
| --- | --- |
| `Unnamed: 0` | `object` |
| `the weight of the stock-picking concept` | `object` |
| `Unnamed: 2` | `object` |
| `Unnamed: 3` | `object` |
| `Unnamed: 4` | `object` |
| `Unnamed: 5` | `object` |
| `Unnamed: 6` | `object` |
| `the original investment performance indicator` | `object` |
| `Unnamed: 8` | `object` |
| `Unnamed: 9` | `object` |
| `Unnamed: 10` | `object` |
| `Unnamed: 11` | `object` |
| `Unnamed: 12` | `object` |
| `the normalized  investment performance indicator` | `object` |
| `Unnamed: 14` | `object` |
| `Unnamed: 15` | `object` |
| `Unnamed: 16` | `object` |
| `Unnamed: 17` | `object` |
| `Unnamed: 18` | `object` |

### 每列缺失值数量

| column | value |
| --- | --- |
| `Unnamed: 0` | `0` |
| `the weight of the stock-picking concept` | `0` |
| `Unnamed: 2` | `0` |
| `Unnamed: 3` | `0` |
| `Unnamed: 4` | `0` |
| `Unnamed: 5` | `0` |
| `Unnamed: 6` | `0` |
| `the original investment performance indicator` | `0` |
| `Unnamed: 8` | `0` |
| `Unnamed: 9` | `0` |
| `Unnamed: 10` | `0` |
| `Unnamed: 11` | `0` |
| `Unnamed: 12` | `0` |
| `the normalized  investment performance indicator` | `0` |
| `Unnamed: 14` | `0` |
| `Unnamed: 15` | `0` |
| `Unnamed: 16` | `0` |
| `Unnamed: 17` | `0` |
| `Unnamed: 18` | `0` |

### 前 5 行样例

```text
Unnamed: 0 the weight of the stock-picking concept  Unnamed: 2  Unnamed: 3                              Unnamed: 4           Unnamed: 5             Unnamed: 6 the original investment performance indicator    Unnamed: 8      Unnamed: 9 Unnamed: 10   Unnamed: 11   Unnamed: 12 the normalized  investment performance indicator   Unnamed: 14     Unnamed: 15 Unnamed: 16   Unnamed: 17   Unnamed: 18
        ID                              Large B/P   Large ROE   Large S/P   Large Return Rate in the last quarter   Large Market Value   Small systematic Risk                                 Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate                                    Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate
         1                                       1           0           0                                       0                    0                      0                                      0.221805      0.062884         1.58044     0.16436          0.65           0.8                                         0.647161      0.688251             0.8         0.8      0.457143          0.65
         2                                       0           1           0                                       0                    0                      0                                      0.142353      0.039906        1.207561    0.120847          0.55           0.8                                         0.492034      0.494779        0.488481    0.460754      0.285714          0.65
         3                                       0           0           1                                       0                    0                      0                                      0.295726      0.076156        1.316862    0.147754          0.65          0.85                                         0.791489           0.8        0.579796     0.67053      0.457143         0.725
         4                                       0           0           0                                       1                    0                      0                                      0.002086       0.01247        1.437964    0.159745           0.5          0.55                                         0.218169      0.263772        0.680969    0.764019           0.2         0.275
```

### 带 % 的字符串

- 是否出现：否
- 出现列：
- none

### 非数值字段

- 是否存在：是
- 字段：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

## Sheet: 2nd period

- 行数：64
- 列数：19
- 列名：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

### 每列 dtype

| column | value |
| --- | --- |
| `Unnamed: 0` | `object` |
| `the weight of the stock-picking concept` | `object` |
| `Unnamed: 2` | `object` |
| `Unnamed: 3` | `object` |
| `Unnamed: 4` | `object` |
| `Unnamed: 5` | `object` |
| `Unnamed: 6` | `object` |
| `the original investment performance indicator` | `object` |
| `Unnamed: 8` | `object` |
| `Unnamed: 9` | `object` |
| `Unnamed: 10` | `object` |
| `Unnamed: 11` | `object` |
| `Unnamed: 12` | `object` |
| `the normalized  investment performance indicator` | `object` |
| `Unnamed: 14` | `object` |
| `Unnamed: 15` | `object` |
| `Unnamed: 16` | `object` |
| `Unnamed: 17` | `object` |
| `Unnamed: 18` | `object` |

### 每列缺失值数量

| column | value |
| --- | --- |
| `Unnamed: 0` | `0` |
| `the weight of the stock-picking concept` | `0` |
| `Unnamed: 2` | `0` |
| `Unnamed: 3` | `0` |
| `Unnamed: 4` | `0` |
| `Unnamed: 5` | `0` |
| `Unnamed: 6` | `0` |
| `the original investment performance indicator` | `0` |
| `Unnamed: 8` | `0` |
| `Unnamed: 9` | `0` |
| `Unnamed: 10` | `0` |
| `Unnamed: 11` | `0` |
| `Unnamed: 12` | `0` |
| `the normalized  investment performance indicator` | `0` |
| `Unnamed: 14` | `0` |
| `Unnamed: 15` | `0` |
| `Unnamed: 16` | `0` |
| `Unnamed: 17` | `0` |
| `Unnamed: 18` | `0` |

### 前 5 行样例

```text
Unnamed: 0 the weight of the stock-picking concept  Unnamed: 2  Unnamed: 3                              Unnamed: 4           Unnamed: 5             Unnamed: 6 the original investment performance indicator    Unnamed: 8      Unnamed: 9 Unnamed: 10   Unnamed: 11   Unnamed: 12 the normalized  investment performance indicator   Unnamed: 14     Unnamed: 15 Unnamed: 16   Unnamed: 17   Unnamed: 18
        ID                              Large B/P   Large ROE   Large S/P   Large Return Rate in the last quarter   Large Market Value   Small systematic Risk                                 Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate                                    Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate
         1                                       1           0           0                                       0                    0                      0                                      0.077004     -0.015932        0.736939    0.095878           0.6           0.3                                         0.227755       0.50754        0.244336    0.316609      0.371429           0.4
         2                                       0           1           0                                       0                    0                      0                                      0.167495     -0.017357        1.169841    0.103008           0.7           0.4                                         0.589132      0.481622        0.587008    0.367016      0.542857           0.6
         3                                       0           0           1                                       0                    0                      0                                      0.097648     -0.025967        1.049221    0.111338          0.55           0.3                                         0.310197      0.325059        0.491529     0.42591      0.285714           0.4
         4                                       0           0           0                                       1                    0                      0                                      0.203422     -0.016849        1.438916    0.164251           0.7           0.4                                         0.732604      0.490854             0.8         0.8      0.542857           0.6
```

### 带 % 的字符串

- 是否出现：否
- 出现列：
- none

### 非数值字段

- 是否存在：是
- 字段：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

## Sheet: 1st period

- 行数：64
- 列数：19
- 列名：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

### 每列 dtype

| column | value |
| --- | --- |
| `Unnamed: 0` | `object` |
| `the weight of the stock-picking concept` | `object` |
| `Unnamed: 2` | `object` |
| `Unnamed: 3` | `object` |
| `Unnamed: 4` | `object` |
| `Unnamed: 5` | `object` |
| `Unnamed: 6` | `object` |
| `the original investment performance indicator` | `object` |
| `Unnamed: 8` | `object` |
| `Unnamed: 9` | `object` |
| `Unnamed: 10` | `object` |
| `Unnamed: 11` | `object` |
| `Unnamed: 12` | `object` |
| `the normalized  investment performance indicator` | `object` |
| `Unnamed: 14` | `object` |
| `Unnamed: 15` | `object` |
| `Unnamed: 16` | `object` |
| `Unnamed: 17` | `object` |
| `Unnamed: 18` | `object` |

### 每列缺失值数量

| column | value |
| --- | --- |
| `Unnamed: 0` | `0` |
| `the weight of the stock-picking concept` | `0` |
| `Unnamed: 2` | `0` |
| `Unnamed: 3` | `0` |
| `Unnamed: 4` | `0` |
| `Unnamed: 5` | `0` |
| `Unnamed: 6` | `0` |
| `the original investment performance indicator` | `0` |
| `Unnamed: 8` | `0` |
| `Unnamed: 9` | `0` |
| `Unnamed: 10` | `0` |
| `Unnamed: 11` | `0` |
| `Unnamed: 12` | `0` |
| `the normalized  investment performance indicator` | `0` |
| `Unnamed: 14` | `0` |
| `Unnamed: 15` | `0` |
| `Unnamed: 16` | `0` |
| `Unnamed: 17` | `0` |
| `Unnamed: 18` | `0` |

### 前 5 行样例

```text
Unnamed: 0 the weight of the stock-picking concept  Unnamed: 2  Unnamed: 3                              Unnamed: 4           Unnamed: 5             Unnamed: 6 the original investment performance indicator    Unnamed: 8      Unnamed: 9 Unnamed: 10   Unnamed: 11   Unnamed: 12 the normalized  investment performance indicator   Unnamed: 14     Unnamed: 15 Unnamed: 16   Unnamed: 17   Unnamed: 18
        ID                              Large B/P   Large ROE   Large S/P   Large Return Rate in the last quarter   Large Market Value   Small systematic Risk                                 Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate                                    Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate
         1                                       1           0           0                                       0                    0                      0                                      0.255357      0.020778        0.975575    0.081426           0.8           0.6                                         0.624791      0.713672        0.381541    0.688242          0.56           0.5
         2                                       0           1           0                                       0                    0                      0                                      0.249602       0.00396        1.350801    0.077498          0.85          0.75                                          0.59928      0.430547        0.737417    0.633989          0.68         0.725
         3                                       0           0           1                                       0                    0                      0                                      0.231246      0.013456        1.040006    0.087826           0.8           0.4                                         0.517916      0.590403        0.442649    0.776619          0.56           0.2
         4                                       0           0           0                                       1                    0                      0                                      0.203809       -0.0026        1.291899    0.088624           0.7           0.6                                         0.396296      0.320119        0.681552    0.787637          0.32           0.5
```

### 带 % 的字符串

- 是否出现：否
- 出现列：
- none

### 非数值字段

- 是否存在：是
- 字段：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

## Sheet: all period

- 行数：64
- 列数：19
- 列名：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

### 每列 dtype

| column | value |
| --- | --- |
| `Unnamed: 0` | `object` |
| `the weight of the stock-picking concept` | `object` |
| `Unnamed: 2` | `object` |
| `Unnamed: 3` | `object` |
| `Unnamed: 4` | `object` |
| `Unnamed: 5` | `object` |
| `Unnamed: 6` | `object` |
| `the original investment performance indicator` | `object` |
| `Unnamed: 8` | `object` |
| `Unnamed: 9` | `object` |
| `Unnamed: 10` | `object` |
| `Unnamed: 11` | `object` |
| `Unnamed: 12` | `object` |
| `the normalized  investment performance indicator` | `object` |
| `Unnamed: 14` | `object` |
| `Unnamed: 15` | `object` |
| `Unnamed: 16` | `object` |
| `Unnamed: 17` | `object` |
| `Unnamed: 18` | `object` |

### 每列缺失值数量

| column | value |
| --- | --- |
| `Unnamed: 0` | `0` |
| `the weight of the stock-picking concept` | `0` |
| `Unnamed: 2` | `0` |
| `Unnamed: 3` | `0` |
| `Unnamed: 4` | `0` |
| `Unnamed: 5` | `0` |
| `Unnamed: 6` | `0` |
| `the original investment performance indicator` | `0` |
| `Unnamed: 8` | `0` |
| `Unnamed: 9` | `0` |
| `Unnamed: 10` | `0` |
| `Unnamed: 11` | `0` |
| `Unnamed: 12` | `0` |
| `the normalized  investment performance indicator` | `0` |
| `Unnamed: 14` | `0` |
| `Unnamed: 15` | `0` |
| `Unnamed: 16` | `0` |
| `Unnamed: 17` | `0` |
| `Unnamed: 18` | `0` |

### 前 5 行样例

```text
Unnamed: 0 the weight of the stock-picking concept  Unnamed: 2  Unnamed: 3                              Unnamed: 4           Unnamed: 5             Unnamed: 6 the original investment performance indicator    Unnamed: 8      Unnamed: 9 Unnamed: 10   Unnamed: 11   Unnamed: 12 the normalized  investment performance indicator   Unnamed: 14     Unnamed: 15 Unnamed: 16   Unnamed: 17   Unnamed: 18
        ID                              Large B/P   Large ROE   Large S/P   Large Return Rate in the last quarter   Large Market Value   Small systematic Risk                                 Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate                                    Annual Return Excess Return Systematic Risk  Total Risk Abs. Win Rate Rel. Win Rate
         1                                       1           0           0                                       0                    0                      0                                         0.139          0.01            1.33       0.149         0.663         0.525                                         0.531875      0.478116        0.738015         0.8          0.52      0.411765
         2                                       0           1           0                                       0                    0                      0                                         0.143          0.01            1.17       0.108         0.663          0.65                                         0.549712      0.487595        0.571579    0.412231          0.52      0.764706
         3                                       0           0           1                                       0                    0                      0                                         0.173         0.018             1.3       0.144         0.638         0.513                                         0.692625      0.629895        0.703051    0.756879          0.44      0.376471
         4                                       0           0           0                                       1                    0                      0                                         0.096        -0.002            1.39       0.144         0.613         0.475                                         0.324351      0.255634             0.8    0.756046          0.36      0.270588
```

### 带 % 的字符串

- 是否出现：否
- 出现列：
- none

### 非数值字段

- 是否存在：是
- 字段：
- `Unnamed: 0`
- `the weight of the stock-picking concept`
- `Unnamed: 2`
- `Unnamed: 3`
- `Unnamed: 4`
- `Unnamed: 5`
- `Unnamed: 6`
- `the original investment performance indicator`
- `Unnamed: 8`
- `Unnamed: 9`
- `Unnamed: 10`
- `Unnamed: 11`
- `Unnamed: 12`
- `the normalized  investment performance indicator`
- `Unnamed: 14`
- `Unnamed: 15`
- `Unnamed: 16`
- `Unnamed: 17`
- `Unnamed: 18`

## Sheet: Time frame

- 行数：5
- 列数：4
- 列名：
- `Time-frame`
- `The beginning time of the 1st holding period`
- `The beginning time of the 20th holding period`
- `The length of period`

### 每列 dtype

| column | value |
| --- | --- |
| `Time-frame` | `str` |
| `The beginning time of the 1st holding period` | `str` |
| `The beginning time of the 20th holding period` | `str` |
| `The length of period` | `str` |

### 每列缺失值数量

| column | value |
| --- | --- |
| `Time-frame` | `0` |
| `The beginning time of the 1st holding period` | `0` |
| `The beginning time of the 20th holding period` | `0` |
| `The length of period` | `0` |

### 前 5 行样例

```text
    Time-frame The beginning time of the 1st holding period The beginning time of the 20th holding period   The length of period
The all-period                                    1990/9/30                                     2010/6/30 80 quarters (20 years)
The 1st period                                    1990/9/30                                     1995/6/30  20 quarters (5 years)
The 2nd period                                    1995/9/30                                     2000/6/30  20 quarters (5 years)
The 3rd period                                    2000/9/30                                     2005/6/30  20 quarters (5 years)
The 4th period                                    2005/9/30                                     2010/6/30  20 quarters (5 years)
```

### 带 % 的字符串

- 是否出现：否
- 出现列：
- none

### 非数值字段

- 是否存在：是
- 字段：
- `Time-frame`
- `The beginning time of the 1st holding period`
- `The beginning time of the 20th holding period`
- `The length of period`
