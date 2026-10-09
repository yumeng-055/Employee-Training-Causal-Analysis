# Employee Training Causal Analysis

**Retail performance and causal analytics | Python · Panel data · Fixed effects · Difference-in-Differences · Reproducible reporting**

This case study uses **1,200 monthly observations from 50 stores across 2024–2025** to evaluate employee training introduced in January 2025. It compares pooled OLS, store fixed effects, and random effects, then uses two-way fixed effects difference-in-differences (TWFE DID) to estimate relative sales changes. The panel includes 25 trained and 25 control stores, with 12 months before and 12 months after the intervention.

*An individual academic project using course-provided panel data and a simulated retail management brief. Numerical findings are verified; rollout recommendations and pilot measures are proposals for further validation.*

- **Business question:** Did employee training improve monthly store sales enough to support a phased expansion of the programme?
- **Key finding:** TWFE DID estimates **+5.19 monthly sales units**, with a store-clustered 95% confidence interval of **[4.44, 5.94]** and **p < 0.001**. Under the DID assumptions, this supports a monitored pilot in comparable stores, followed by a cost and margin evaluation before broader rollout.
- **Project contribution:** Validate a monthly store panel, compare pooled and within-store associations, estimate the training effect with uncertainty, and translate the evidence into rollout recommendations with proposed validation measures.
- **Core strengths:** Python data analysis, econometric programme evaluation, data quality controls, reproducible reporting, and communication of business decisions with uncertainty.

[Case study](report/employee_training_analysis_report.md) · [Complete notebook](notebooks/employee_training_causal_analysis.ipynb) · [Data dictionary](data/README.md) · [Model comparison](outputs/tables/model_comparison.csv)

![Case study overview](screenshots/project_overview.png)

## 1. Business Problem

Management needs to decide whether to expand employee training. A simple before-and-after comparison cannot distinguish training from broader sales growth, and trained stores may differ systematically from controls. The analysis therefore compares changes in both groups while accounting for stable store characteristics and common monthly shocks.

The intended reader is a retail operations manager deciding whether to fund a further pilot. The analytical objective is to estimate incremental monthly sales for trained stores, assess the credibility of that estimate, and identify the information needed for a scaling decision. Deliverables include a reproducible analysis, a management report, and a proposed monitoring framework.

The workflow connects a decision to measurable evidence: define the store-month sales outcome, validate the panel, compare changes with a control group, assess uncertainty and assumptions, and specify how a future pilot would inform the next rollout decision.

## 2. Executive Summary

- **Data:** a balanced, course-provided monthly panel spanning 2024–2025; 25 trained and 25 control stores.
- **Approach:** descriptive comparisons → OLS → store FE and RE → TWFE DID → visual parallel-trends assessment.
- **Finding:** the treatment interaction estimates a +5.19-unit effect. The model explains approximately 78.6% of observed sales variation, including fixed effects; adjusted R-squared is approximately 0.772.
- **Decision:** pilot expansion in similar stores, monitor outcomes and operational indicators, and assess economics before scaling.
- **Scope:** the main interpretation uses an identified TWFE model and explicit causal assumptions. IV/2SLS was proposed but **never empirically estimated**. See [the complete analysis report](report/employee_training_analysis_report.md).

## 3. Key Finding

Under parallel trends, no anticipation, no relevant spillovers, and no confounding group-specific shocks, the DID estimate suggests that training increased average monthly store sales by approximately **5.19 dataset units**. This is an estimated effect within the observed sample, not a realised business outcome or an ROI estimate.

Average price is fully absorbed by store and month effects in this dataset. The identified TWFE model therefore omits its redundant separate coefficient and gives the same training estimate, with a store-clustered 95% interval of **[4.44, 5.94]**. See [the complete analysis report](report/employee_training_analysis_report.md).

The estimate describes the average relative monthly change for treated stores in this sample. It is expressed in sales units, not a percentage uplift, and does not imply that every store gains the same amount. The confidence interval quantifies model-based uncertainty; it does not account for bias from violated causal assumptions.

## 4. Data

The supplied data contain store identifiers, observation month, training-group and post-period indicators, sales, staffing, average price, and competitor count. Month 13 marks the intervention. The pipeline validates coverage and missing values and compares the CSV with the unchanged Excel workbook.

No data are invented or removed. Sales currency and measurement scale are not established, so effects are reported in dataset units. The data are course-provided; real-company provenance, simulation status, and public redistribution rights are not asserted. See [data documentation](data/README.md).

### 4.1 Analytical Data Definitions

| Definition | Rule used in the analysis | Evidence |
|---|---|---|
| **Observation unit and key** | One row per store and month; `(store_id, month)` must be unique | [Data checks](src/data_processing.py) |
| **Coverage** | 50 stores, each observed for all 24 months; all required analysis values present | [Validation output](outputs/tables/data_quality.csv) |
| **Treatment and timing** | Binary treatment remains constant within store; the post period starts in month 13 | [Data definitions](data/README.md) |
| **Hypothesis-test unit** | Average the 12 post-period observations for each store before comparing 25 stores per group | [Welch test implementation](src/descriptive_analysis.py) |
| **Main effect and inference** | TWFE training interaction in monthly sales units, with 50 store clusters and a normal-reference confidence interval | [DID results](outputs/tables/twfe_did_results.csv) |

These definitions keep descriptive summaries, model estimates, and the report aligned. The workflow fails when required panel checks or source-data consistency checks fail.

## 5. Analytical Approach

### 5.1 Descriptive Analysis

| Group   | Pre-training mean sales | Post-training mean sales |
| ------- | ----------------------: | -----------------------: |
| Control |                   56.91 |                    58.60 |
| Treated |                   56.48 |                    63.36 |

The larger increase in trained stores is descriptive evidence. A Welch test compares the 12-month post-training average for each store, using 25 independent store summaries per group: **p ≈ 0.0013**. It does not control for selection or time-varying confounding.

### 5.2 Regression Analysis

OLS uses `treated`, `post`, `staff_num`, `avg_price`, and `competitor_num`. The `treated` coefficient of **2.0243** is a conditional group difference across the full sample, not the training effect. VIF, residual Q-Q, and residual-versus-fitted plots support model inspection without claiming that graphical diagnostics prove all assumptions.

### 5.3 Panel Data Models

Store FE controls for persistent store differences. The classical pooled-versus-FE F comparison gives **F = 50.22 (p < 0.001)**, providing evidence that store-level heterogeneity matters under classical test assumptions. It is not a cluster-robust joint test.

**Store FE is retained primarily because the research design focuses on within-store changes over time.** Persistent unobserved differences across stores are substantively important, and store fixed effects control time-invariant store heterogeneity.

`treated` is constant within store and is absorbed by store effects. FE estimates `post = 2.6919` and `avg_price = 2.1002`; staffing and competitor count lose their OLS significance. Some pooled associations may reflect persistent differences between stores rather than within-store changes. The FE `post` coefficient describes an overall period change, including training exposure; it is not a control-group-only secular trend.

`RandomEffects` gives `treated = 1.8376` (p ≈ 0.194). The classical Hausman comparison has an indefinite covariance difference, so valid chi-square inference is unavailable. Store FE is selected on substantive grounds: controlling persistent store differences is appropriate for a non-random training programme. The analysis does not claim a valid Hausman rejection of RE consistency.

### 5.4 Difference-in-Differences

```text
sales_it = store_FE_i + month_FE_t + beta × (treated_i × post_t) + error_it
```

Standard errors are clustered by store to allow correlated errors across a store's monthly observations. `treated` and `post` main effects are absorbed by store and month effects respectively. Staffing and competitor count are excluded from the parsimonious specification; their earlier insignificance alone does not establish that omitted variables are harmless.

Average price varies as a store-specific level plus a common monthly change, so its variation is absorbed by the fixed effects. No separate price coefficient is estimated in TWFE. The [complete report](report/employee_training_analysis_report.md) presents the identified model and uncertainty estimates.

### 5.5 Parallel Trends

![Monthly store sales trends](outputs/figures/monthly_sales_trends.png)

Before January 2025, group-average sales move broadly together; afterward, trained stores diverge upward. This visual check and the monthly difference table are consistent with parallel trends, but **do not prove the unobserved counterfactual assumption**. No formal event-study, placebo, or spillover regression is claimed as completed.

### 5.6 Potential IV/2SLS Extension

Management could select stores into training based on unobserved potential or motivation. Distance to the nearest training centre was proposed as an instrument: the first stage would predict training participation from distance and exogenous controls; the second stage would relate sales to instrumented training exposure using appropriate IV inference.

**The IV/2SLS model was not estimated because the required instrument data were unavailable.** No IV coefficient or first-stage F-statistic is reported. Distance relevance and exclusion remain hypotheses, especially because location may affect demand. A panel extension would instrument `treated × post` using `distance × post`, subject to a defensible exclusion restriction.

## 6. Key Results

| Result | Estimate | Interpretation |
|---|---:|---|
| OLS `treated` | 2.0243 | Conditional group difference |
| Store FE `post` | 2.6919 | Within-store period association |
| Store FE `avg_price` | 2.1002 | Within-store association; p ≈ 0.012 |
| TWFE `treated:post` | **5.1852** | Training estimate under DID assumptions |
| RE `treated` | 1.8376 | Conditional group difference; p ≈ 0.194 |

![Model comparison](outputs/figures/model_comparison.png)

The group coefficients and DID interaction answer different questions and should not be read as interchangeable treatment estimates. FE has no separate `treated` coefficient. Estimator-specific R-squared measures are not directly comparable.

Full precision and uncertainty are available in [descriptive statistics](outputs/tables/descriptive_statistics.csv), [OLS results](outputs/tables/ols_results.csv), and [the DID results](outputs/tables/twfe_did_results.csv). The [complete report](report/employee_training_analysis_report.md) includes the OLS, FE, and RE comparison and interpretation.

## 7. Business Recommendations

1. **Expand through a controlled pilot.** The positive DID estimate supports testing training in comparable stores. Where feasible, randomise eligible stores to immediate training or a later rollout, retaining all stores in their assigned groups for evaluation. Assess incremental monthly sales with uncertainty before broad expansion.
2. **Monitor outcomes and implementation.** The difference between pooled and within-store associations makes consistent store-level tracking important. Record sales, staffing, price, promotions, assignment, and attendance so that operational changes and delivery quality can be evaluated alongside outcomes.
3. **Test customer-value initiatives separately.** Positive price associations suggest questions about product presentation and higher-value recommendations. Evaluate these initiatives separately, or explicitly design a combined intervention, so their effects can be distinguished from training.

### 7.1 Proposed Pilot Scorecard

These measures are proposals for a future pilot, not measured rollout outcomes or implemented dashboards.

| Decision measure | Definition and use | Additional data required |
|---|---|---|
| **Incremental monthly sales** | Difference in average sales changes between assigned pilot and comparison stores over a pre-specified baseline and follow-up window; report the estimate and confidence interval | Future store-month sales and assignment dates |
| **Training completion** | Staff completing the programme divided by staff assigned to it, by store and training cohort; assess delivery without excluding non-completers from the store-level effect estimate | Staff assignment and completion records |
| **Incremental contribution after training costs** | Estimate incremental revenue and contribution using documented sales units, margins, and programme costs before making a scaling decision | Sales-unit definition, transaction revenue, margins, and direct and indirect training costs |

Proceed toward expansion only if the pilot's estimated benefit is commercially meaningful relative to cost and operational disruption. Define the evaluation window, decision criteria, and service or staffing guardrails before observing results; the current data do not support a numerical ROI target.

## 8. Limitations

- Training was not randomly assigned; selection and unobserved time-varying differences may remain.
- Concurrent interventions, external shocks, anticipation, and spillovers can violate DID assumptions.
- Visual pre-trends are a limited diagnostic, and the observation window contains only 12 pre-treatment and 12 post-treatment months.
- Price may respond to training, and its separate TWFE coefficient is unidentified; control selection is not a guarantee against omitted-variable bias.
- Findings may not generalise beyond the 50 stores. Training costs and margins are absent, so no profitability or ROI claim is possible.
- The Hausman comparison does not support valid chi-square inference; FE is retained as a substantive design choice.

**Next data priorities:** intervention assignment and attendance records, concurrent promotions, verified sales units, and training costs and margins. With those inputs, a future evaluation could assess implementation quality, confounding interventions, and economics. Formal event-study and placebo analyses remain potential extensions rather than completed evidence.

## 9. Repository Navigation

### 9.1 Project Structure

```text
employee-training-causal-analysis/
├── README.md, requirements.txt, .gitignore
├── data/                 # unchanged workbook, CSV, documentation
├── notebooks/            # executed English workflow
├── src/                  # reusable data, model, and visualisation modules
├── outputs/
│   ├── figures/          # trends, distribution, diagnostics, model comparison
│   └── tables/           # model estimates, diagnostics, data quality, provenance
├── report/               # final complete English analysis report
└── screenshots/          # key analytical outputs for presentation
```

### 9.2 File Navigation

| Location | Contents |
|---|---|
| [Analysis notebook](notebooks/employee_training_causal_analysis.ipynb) | Complete English workflow with executed results, charts, and interpretation |
| [Case study report](report/employee_training_analysis_report.md) | Business question, methodology, statistical evidence, limitations, and management recommendations |
| [Dataset](data/employee_training_data.csv) | The complete panel of 50 stores and 1,200 monthly observations |
| [Data documentation](data/README.md) | Variable definitions, observation period, source information, and preprocessing |
| [Source code](src/) | Reusable functions for data preparation, hypothesis testing, regression, panel models, DID, and visualisation |
| [Result tables](outputs/tables/) | Descriptive statistics, model estimates, confidence intervals, and model diagnostics |
| [Figures](outputs/figures/) | Monthly sales trends, sales distributions, regression diagnostics, and model comparison |
| [Presentation images](screenshots/) | Key finding, monthly trends, and model results for a quick project overview |
| [Data quality checks](outputs/tables/data_quality.csv) | Panel coverage, missing values, unique store-month keys, and treatment consistency |
| [Dependencies](requirements.txt) | Package versions for reproducing the analysis |

## 10. How to Run

Requires **Python 3.12**. Download or clone this repository and open a terminal in its root directory:

```bash
python -m venv .venv
```

Activate on Windows PowerShell with `.\.venv\Scripts\Activate.ps1`, or on macOS/Linux with `source .venv/bin/activate`. Then:

```bash
python -m pip install -r requirements.txt
python -m src.run_analysis
python -m jupyterlab
```

Open `notebooks/employee_training_causal_analysis.ipynb`, select the virtual environment's Python kernel, and run all cells in order. The notebook also calls the full pipeline, so it can run independently of the command-line analysis step. Outputs are overwritten reproducibly; the source data are not overwritten.

For a headless notebook execution that uses the current interpreter:

```bash
python -m src.execute_notebook
```

The pipeline validates the panel structure, source-data consistency, and TWFE design rank. The modular pipeline and all 14 code cells of the English notebook have executed successfully in a clean environment installed from `requirements.txt`. The [complete report](report/employee_training_analysis_report.md) documents the final findings and methodological qualifications.

### 10.1 Reproducible Reporting Outputs

`python -m src.run_analysis` regenerates the result tables, charts, presentation images, and a [reproducibility manifest](outputs/tables/reproducibility_manifest.json) recording package versions and data hashes. Figures and tables are generated from the same fitted models used for interpretation. This is an implemented local reporting workflow; monitoring the outcomes of a future rollout remains a proposed business process.

## 11. Technologies and Analytical Skills

**Python · Econometrics · Causal Inference · Data Quality · Reporting Automation · Business Analytics**

| Capability | Tools and methods | Application and reviewable evidence |
|---|---|---|
| **Data preparation and validation** | pandas, NumPy, openpyxl | Validate the panel and source consistency: [data processing](src/data_processing.py), [quality checks](outputs/tables/data_quality.csv) |
| **Statistical analysis** | SciPy, statsmodels | Compare store-level outcomes and assess OLS diagnostics: [descriptive analysis](src/descriptive_analysis.py), [regression functions](src/regression_models.py), [Welch test](outputs/tables/welch_ttest.csv) |
| **Panel modelling** | linearmodels | Separate within-store associations from cross-store differences: [panel estimators](src/panel_models.py), [model comparison](outputs/tables/model_comparison.csv) |
| **Causal inference** | statsmodels, TWFE DID | Estimate relative changes with fixed effects and clustered uncertainty: [DID functions](src/did_analysis.py), [effect and confidence interval](outputs/tables/twfe_did_results.csv) |
| **Data visualisation** | Matplotlib | Communicate sales patterns and uncertainty: [visualisation functions](src/visualization.py), [monthly trends](outputs/figures/monthly_sales_trends.png) |
| **Reproducible analysis** | Jupyter, pathlib, modular Python | Regenerate outputs with portable paths and pinned dependencies: [analysis entry point](src/run_analysis.py), [executed notebook](notebooks/employee_training_causal_analysis.ipynb) |
| **Reporting automation** | Python, CSV exports, saved PNGs | Generate consistent tables, figures, and presentation images through one local command: [reporting workflow](src/run_analysis.py), [version and data manifest](outputs/tables/reproducibility_manifest.json) |
| **Business communication** | Case study reporting | Connect evidence to rollout choices, proposed KPIs, and validation: [management implications](report/employee_training_analysis_report.md#8-management-implications) |

The evidence covers a 1,200-row retail panel and an observational programme evaluation. The controlled pilot design is a proposal; the completed causal analysis is DID on the supplied panel.

Dependencies are pinned in [requirements.txt](requirements.txt). Notebook automation uses nbformat, nbclient, and ipykernel to execute the workflow without an interactive session.
