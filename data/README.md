# Dataset

This course-provided dataset supports a case study of employee training and store sales. It is not claimed to be public, collected by the author, or verified real company data. The source does not establish whether the records were simulated for teaching. No synthetic observations have been added by this project.

The balanced panel covers 50 stores, with 24 monthly observations per store (1,200 rows). There are 25 treated and 25 control stores. Following the supplied observation-period metadata, months 1–12 represent January–December 2024 and months 13–24 represent January–December 2025; training begins in month 13. These calendar labels are mapped from supplied metadata rather than collected date fields.

| Variable | Meaning |
|---|---|
| `store_id` | Store identifier |
| `month` | Observation month, 1–24 |
| `treated` | 1 for training-group stores, 0 for control stores |
| `post` | 1 from month 13 onward, 0 beforehand |
| `staff_num` | Number of staff |
| `avg_price` | Average price indicator |
| `competitor_num` | Number of competitors |
| `sales` | Monthly store sales outcome in the supplied dataset's units |

Sales units and currency are not documented well enough to translate results into revenue, profit, or return on investment. Distance to a training centre, training costs, store coordinates, and other intervention indicators are unavailable.

`original_course_data.xlsx` is a byte-for-byte copy of the provided workbook. `employee_training_data.csv` exports its first worksheet without filtering, imputation, rounding, winsorisation, or modification of source values. The pipeline checks the CSV against the workbook, validates unique store-month keys, missing values, treatment status, and balanced-panel coverage. Sorting for panel estimation affects row order only.

The files are included for the requested portfolio. Public redistribution rights have not been established by the materials supplied; no open-data licence is asserted.

The first analysis run creates the CSV if absent. Subsequent runs verify it rather than overwrite it. SHA-256 hashes and package versions are recorded in `outputs/tables/reproducibility_manifest.json`.
